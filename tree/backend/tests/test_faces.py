import os
from unittest import TestCase

import face_recognition

import tree.backend.constants as constants
import tree.backend.faces as faces


class TestFaces(TestCase):
    def setUp(self):
        pass

    def test_create_face_from_image(self):
        test_image_filepath = os.path.join(constants.test_images_filepath, 'yash1.jpg')

        # Create the face object from the image
        face = faces.create_face_from_image(test_image_filepath)

        # Ensure that the original face and the cropped face are both recognized as the same face
        original_image = face_recognition.load_image_file(test_image_filepath)
        original_encoding = face_recognition.face_encodings(original_image)[0]
        results = face_recognition.compare_faces([original_encoding], face.encoding)

        # We should only find one face
        self.assertTrue(len(results) == 1)
        # If this is true, then the faces are the same
        self.assertTrue(results[0])

        # Ensure the id and filename are constructed correctly
        self.assertEqual(face.full_image_filename_from_id(face._id), face.full_image_filename)
        self.assertEqual(face.cropped_image_filename_from_id(face._id), face.cropped_image_filename)
