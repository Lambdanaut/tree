import os
from unittest import TestCase

import face_recognition

import tree.backend.constants as constants
import tree.backend.faces as faces


class TestFaces(TestCase):
    def setUp(self):
        self.test_yash_image_filepath1 = os.path.join(constants.test_images_filepath, 'yash1.jpg')
        self.test_yash_image_filepath2 = os.path.join(constants.test_images_filepath, 'yash2.jpg')
        self.test_joshua_image_filepath1 = os.path.join(constants.test_images_filepath, 'joshua1.jpg')
        self.test_joshua_image_filepath2 = os.path.join(constants.test_images_filepath, 'joshua2.jpg')

    def test_create_face_from_image(self):
        # Create the face object from the image
        face = faces.create_face_from_image(self.test_yash_image_filepath1)

        # Ensure that the original face and the cropped face are both recognized as the same face
        original_image = face_recognition.load_image_file(self.test_yash_image_filepath1)
        original_encoding = face_recognition.face_encodings(original_image)[0]
        results = face_recognition.compare_faces([original_encoding], face.encoding)

        # We should only find one face
        self.assertTrue(len(results) == 1)
        # If this is true, then the faces are the same
        self.assertTrue(results[0])

        # Ensure the id and filename are constructed correctly
        self.assertEqual(face.full_image_filename_from_id(face._id), face.full_image_filename)
        self.assertEqual(face.cropped_image_filename_from_id(face._id), face.cropped_image_filename)

    def test_get_face_from_image(self):
        f = faces.Faces()

        # Create the face objects from the images and add them to the Faces object
        yash_face = f.add_face_from_image(self.test_yash_image_filepath1)
        joshua_face = f.add_face_from_image(self.test_joshua_image_filepath1)

        # Add some messages to the created faces
        yash_messages = ["I love you", "you stinky man you"]
        joshua_messages = ["you're a fuzzy man", "un bee leev a ble!"]

        for message in yash_messages:
            yash_face.add_message(message)
        for message in joshua_messages:
            joshua_face.add_message(message)

        # Get the encodings for the two alternate faces
        yash_face_2 = face_recognition.load_image_file(self.test_yash_image_filepath2)
        joshua_face_2 = face_recognition.load_image_file(self.test_joshua_image_filepath2)
        yash_encoding_2 = face_recognition.face_encodings(yash_face_2)[0]
        joshua_encoding_2 = face_recognition.face_encodings(joshua_face_2)[0]

        # Search the set of faces for these new faces and try to get matches
        yash_matched_face = f.get_face_from_encoding(yash_encoding_2)
        joshua_matched_face = f.get_face_from_encoding(joshua_encoding_2)

        # Assert faces were matched and found
        self.assertTrue(isinstance(yash_matched_face, faces.Face))
        self.assertTrue(isinstance(joshua_matched_face, faces.Face))

        # Assert the ids of the matched faces match what we'd expect
        self.assertEqual(yash_face._id, yash_matched_face._id)
        self.assertEqual(joshua_face._id, joshua_matched_face._id)

        # Assert the messages of the matched faces match what we'd expect
        self.assertEqual(yash_messages, yash_matched_face.messages)
        self.assertEqual(joshua_messages, joshua_matched_face.messages)

        # Assert that consuming messages works as intended
        self.assertEqual(yash_messages[1], yash_matched_face.consume_message())
        self.assertEqual(len(yash_matched_face.messages), 1)
        self.assertEqual(yash_messages[0], yash_matched_face.consume_message())
        self.assertEqual(len(yash_matched_face.messages), 0)
        self.assertEqual(joshua_messages[1], joshua_matched_face.consume_message())
        self.assertEqual(len(joshua_matched_face.messages), 1)
        self.assertEqual(joshua_messages[0], joshua_matched_face.consume_message())
        self.assertEqual(len(joshua_matched_face.messages), 0)

