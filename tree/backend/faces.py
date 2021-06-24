import os
import sys
import uuid
from typing import Union

sys.path.append('.')

import face_recognition
from PIL import Image
import cv2

import tree.backend.constants as constants
import tree.backend.storage.pickle_storage as pickle_storage


class FaceNotFoundException(Exception):
    """Raised if we couldn't detect a face in the provided image"""
    pass


class NoMatchingFaceFoundException(Exception):
    """Raised if we couldn't match the face to any face in a set of faces"""


class PreExistingFaceFoundException(Exception):
    """Raised if we found an already existing match for this face in the set of pre-existing faces"""
    def __init__(self, preexisting_face: "Face", message: Union[str, None] = None):
        self.preexisting_face = preexisting_face
        self.message = message
        super().__init__(message)


def cam_capture() -> (str, str):
    """
    Captures an image from a connected webcam and saves the file to the fresh_photos folder.
    :return: Returns an id used to create the file and the filepath to the saved image.
    """
    vidcap = cv2.VideoCapture(0)
    success, image = vidcap.read()

    _id = str(uuid.uuid4())
    filename = _id + constants.fresh_photos_extension
    filepath = os.path.join(constants.fresh_photos_filepath, filename)

    cv2.imwrite(filepath, image)

    return _id, filepath


def create_face_from_image(
        filepath: str,
        _id: Union[str, None] = None,
        faces: Union["Faces", None] = None,
        save_backup: bool = True
    ) -> "Face":
    """
    Creates a Face object from an image filepath, optionally adding it to a collection of Faces

    :param filepath: filepath of the image to search for faces within
    :param _id: optional id to use for the new Face object
    :param faces: optional Faces object to add the newly created Face to
    :param save_backup: Saves a backup to disk if `faces` is given and this is set to True
    :return: the newly created Face object
    """

    # Load the image into facial recognition
    image = face_recognition.load_image_file(filepath)

    # Find the location of the face(s) in the image
    face_locations = face_recognition.face_locations(image)

    # Check if we could detect a face or not. If not, try again.
    try:
        face_location = face_locations[0]
    except IndexError:
        raise FaceNotFoundException

    # Create an id for the new face
    _id = _id or str(uuid.uuid4())

    # Build an encoding for the face
    encoding = face_recognition.face_encodings(image)[0]

    # Create a new face object using the new image's id and the face's encoding
    face = Face(_id, encoding)

    # If faces was provided, we want to check if we've seen this face before
    if faces is not None:
        try:
            # Search the record of existing faces for this new face
            preexisting_face = faces.get_face_from_encoding(encoding)
        except NoMatchingFaceFoundException:
            # We don't have a record of this new face, so we should continue on to crop and record it
            faces.add_face(face, save_backup=save_backup)
            pass
        else:
            # We've already seen this face before, so we don't want to record it
            raise PreExistingFaceFoundException(preexisting_face)

    # Crop the face in PIL
    top, right, bottom, left = face_location
    crop_face(image, _id, (left, top, right, bottom), flip_horizontally=True)

    return face


def crop_face(image, filename, box, flip_horizontally=False):
    # Load the image into PIL for cropping
    pil_image = Image.fromarray(image)

    # Crop the face in PIL
    cropped_pil_image = pil_image.crop(box)

    if flip_horizontally:
        cropped_pil_image = cropped_pil_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Save the cropped face
    cropped_image_filename = Face.cropped_image_filename_from_id(filename)
    cropped_image_filepath = os.path.join(constants.cropped_faces_filepath, cropped_image_filename)
    cropped_pil_image.save(cropped_image_filepath)


class Face(object):
    def __init__(self, _id: str, encoding):

        self._id: str = _id
        self.encoding = encoding
        self.messages = []
        self._full_image = None  # Use self.full_image to get this
        self._cropped_image = None  # Use self.cropped_image to get this

    @property
    def full_image_filename(self):
        """Returns the filename of the full original image, based on the id"""
        return Face.full_image_filename_from_id(self._id)

    @property
    def cropped_image_filename(self):
        """Returns the filename of the cropped face, based on the id"""
        return Face.cropped_image_filename_from_id(self._id)

    @property
    def full_image(self):
        if self._full_image:
            return self._full_image

        filepath = os.path.join(constants.fresh_photos_filepath, self.full_image_filename)
        image = Image.open(filepath)
        return image

    @property
    def cropped_image(self):
        if self._cropped_image:
            return self._cropped_image

        filepath = os.path.join(constants.cropped_faces_filepath, self.cropped_image_filename)
        image = Image.open(filepath)
        return image

    @staticmethod
    def full_image_filename_from_id(_id: str):
        return _id + constants.fresh_photos_extension

    @staticmethod
    def cropped_image_filename_from_id(_id: str):
        return _id + constants.cropped_face_extension

    def add_message(self, message):
        self.messages.append(message)

    def consume_message(self):
        return self.messages.pop()

    def show_full_image(self):
        self.full_image.show()

    def show_cropped_image(self):
        self.cropped_image.show()


class Faces(object):
    def __init__(self, faces=None, storage=None):
        self.faces = faces or []
        self.storage = storage or pickle_storage.pickle_storage

    def __iter__(self):
        return self.faces.__iter__()

    def __next__(self):
        return self.faces.__next__()

    @property
    def face_encodings(self):
        return (face.encoding for face in self.faces)

    def get_face_from_encoding(self, face_encoding):
        """
        Loops through the list of recorded faces, comparing a given face encoding to each of them.
        Returns the first face that matches it, or raises `NoMatchingFaceFoundException` if none do.

        :param face_encoding: A face encoding to match against
        :return:
        """
        # Loop through the results, returning the first matching result
        results = face_recognition.compare_faces(list(self.face_encodings), face_encoding)
        for result, face in zip(results, self.faces):
            if result:
                return face

        # No match found
        raise NoMatchingFaceFoundException

    def add_face_from_image(self, filepath: str, _id: Union[str, None] = None, save_backup: bool = True) -> "Face":
        """
        Friendly helper that wraps the create_face_from_image to also add the face to this faces object

        :param filepath: filepath to the image of the face to add
        :param _id: optional id string of the face to add
        :param save_backup: save a backup to disk after adding the new face
        :return: The created Face
        """
        created_face = create_face_from_image(filepath, _id, self, save_backup)
        return created_face

    def add_face(self, face, save_backup: bool = True):
        self.faces.append(face)

        # Saves a backup to disk on adding the new face
        if save_backup:
            self.save()

    def snap_face(self, retries: int = 5) -> "Face":
        """
        Tries to find and snap a face from

        :param retries: Number of times to retry taking photos to find a face before raising `FaceNotFoundException`
        :raises FaceNotFoundException:
        :raises PreexistingFaceFoundException:
        :return:
        """
        face = None

        for retry in range(retries):
            _id, snapped_image_filepath = cam_capture()

            try:
                # Face found in snapped image. Continue and return the face
                face = create_face_from_image(snapped_image_filepath, _id, self)
                break

            except FaceNotFoundException:
                # Face couldn't be found. Cleanup the snapped image and try again
                os.remove(snapped_image_filepath)
                continue

        if face is None:
            raise FaceNotFoundException

        return face

    def add_message(self, face: "Face", message: str, save_backup: bool = True):
        """Wrapper to also save when adding a message to a face"""
        face.add_message(message)

        if save_backup:
            self.save()

    def save(self):
        return self.storage.save(self)
