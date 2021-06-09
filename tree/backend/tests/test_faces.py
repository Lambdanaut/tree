import os
from unittest import TestCase

import tree.backend.constants as constants
import tree.backend.faces as faces


class TestFaces(TestCase):
    def setUp(self):
        self.filepath = os.path.join(constants.backup_filepath, constants.pickle_storage_filename)

        # Delete pre-existing backups between tests
        try:
            os.remove(self.filepath)
        except FileNotFoundError:
            pass

    def test_create_face_from_image(self):
        test_image_filepath = os.path.join(constants.test_images_filepath, 'yash1.jpg')
        face = faces.create_face_from_image(test_image_filepath)
        import pdb; pdb.set_trace()

        self.assertTrue([] == [])
