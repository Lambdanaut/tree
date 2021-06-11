import os
import sys
import uuid
from typing import Union

sys.path.append('.')

import face_recognition
from PIL import Image
import cv2

import tree.backend.constants as constants
from tree.backend.storage.pickle_storage import pickle_storage


class FaceNotFoundException(Exception):
    """Raised if we couldn't detect a face in the provided image"""
    pass


class NoMatchingFaceFoundException(Exception):
    """Raised if we couldn't match the face to any face in a set of faces"""


def cam_capture() -> (str, str):
    vidcap = cv2.VideoCapture(0)
    success, image = vidcap.read()

    _id = str(uuid.uuid4())
    filename = _id + constants.fresh_photos_extension
    filepath = os.path.join(constants.fresh_photos_filepath, filename)

    cv2.imwrite(filepath, image)

    return _id, filepath


def snap_face(retries: int = 5) -> "Face":
    face = None

    for retry in range(retries):
        _id, snapped_image_filepath = cam_capture()

        try:
            # Face found in snapped image. Continue and return the face
            face = create_face_from_image(snapped_image_filepath, _id)
            break
        except FaceNotFoundException:
            # Face couldn't be found. Cleanup the snapped image and try again
            os.remove(snapped_image_filepath)
            continue

    if face is None:
        raise FaceNotFoundException

    return face


def create_face_from_image(filepath: str, _id: Union[str, None] = None) -> "Face":
    # Create an id for the new face
    _id = _id or str(uuid.uuid4())

    # Load the image into facial recognition
    image = face_recognition.load_image_file(filepath)

    # Find the location of the face(s) in the image
    face_locations = face_recognition.face_locations(image)

    # Check if we could detect a face or not. If not, try again.
    try:
        face_location = face_locations[0]
    except IndexError:
        raise FaceNotFoundException

    # Re-format the found face location to be used for cropping in PIL
    top, right, bottom, left = face_location
    pil_formatted_face_location = (left, top, right, bottom)

    # Load the image into PIL for cropping
    pil_image = Image.fromarray(image)

    # Crop the face in PIL
    cropped_pil_image = pil_image.crop(pil_formatted_face_location)

    # Build an encoding for the face
    encoding = face_recognition.face_encodings(image)[0]

    # Save the cropped face
    cropped_image_filename = Face.cropped_image_filename_from_id(_id)
    cropped_image_filepath = os.path.join(constants.cropped_faces_filepath, cropped_image_filename)
    cropped_pil_image.save(cropped_image_filepath)

    # Create and return a new face object using the new image's filepath and the face's encoding
    return Face(_id, encoding)


class Face(object):
    def __init__(self, _id: str, encoding):

        self._id: str = _id
        self.encoding = encoding
        self.messages = []

    @property
    def full_image_filename(self):
        """Returns the filename of the full original image, based on the id"""
        return Face.full_image_filename_from_id(self._id)

    @property
    def cropped_image_filename(self):
        """Returns the filename of the cropped face, based on the id"""
        return Face.cropped_image_filename_from_id(self._id)

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


class Faces(object):
    def __init__(self, faces=None):
        self.faces = faces or []

    @property
    def face_encodings(self):
        return (face.encoding for face in self.faces)

    def get_face_from_image(self, filepath: str):
        # Load the image into facial recognition
        image = face_recognition.load_image_file(filepath)
        face_encoding = face_recognition.face_encodings(image)[0]

        results = face_recognition.compare_faces(list(self.face_encodings), face_encoding)
        for result, face in zip(results, self.faces):
            if result:
                return face

        # No match found
        raise NoMatchingFaceFoundException

    def save(self):
        return pickle_storage.save(self)

    def add_face_from_image(self, filepath: str, _id: Union[str, None] = None) -> "Face":
        created_face = create_face_from_image(filepath, _id)
        self.add_face(created_face)
        return created_face

    def add_face(self, face):
        self.faces.append(face)

# snap_face()
