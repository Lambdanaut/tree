import os
import sys
import uuid
from typing import Union

sys.path.append('.')

import face_recognition
from PIL import Image, ImageDraw
import cv2

import tree.backend.constants as constants
from tree.backend.storage.pickle_storage import pickle_storage


def snap_face() -> "Face":
    # cv2.namedWindow("preview")
    vidcap = cv2.VideoCapture(0)
    success, image = vidcap.read()

    filename = str(uuid.uuid4()) + constants.fresh_photos_extension
    filepath = os.path.join(constants.fresh_photos_filepath, filename)

    cv2.imwrite(filepath, image)

    return create_face_from_image(filepath)


def create_face_from_image(filepath: str, _id: Union[str, None] = None) -> "Face":
    # Create an id for the new face
    _id = _id or str(uuid.uuid4())

    # Load the image into facial recognition
    image = face_recognition.load_image_file(filepath)

    # Load the image into PIL for cropping
    pil_image = Image.fromarray(image)

    # Find the location of the face(s) in the image
    face_locations = face_recognition.face_locations(image)
    face_location = face_locations[0]

    # Re-format the found face location to be used for cropping in PIL
    top, right, bottom, left = face_location
    pil_formatted_face_location = (left, top, right, bottom)

    # Crop the face in PIL
    cropped_pil_image = pil_image.crop(pil_formatted_face_location)

    # Build an encoding for the face
    encoding = face_recognition.face_encodings(image)[0]

    # Save the cropped face
    cropped_image_filename = Face.filename_from_id(_id)
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
    def cropped_image_filename(self):
        """Returns the filename of the image, based on the id"""
        return Face.filename_from_id(self._id)

    @staticmethod
    def filename_from_id(_id: str):
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

    def save(self):
        return pickle_storage.save(self)

    def add_face(self):
        pass

snap_face()
