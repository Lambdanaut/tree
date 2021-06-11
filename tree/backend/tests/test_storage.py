import os
from unittest import TestCase

import tree.backend.constants as constants
import tree.backend.faces as faces
from tree.backend.storage.pickle_storage import PickleStorage


class TestStorage(TestCase):
    def setUp(self):
        self.p = PickleStorage(constants.test_pickle_storage_filename)
        self.filepath = os.path.join(constants.backup_filepath, constants.test_pickle_storage_filename)

    def test_load_without_existing_backup(self):
        loaded_data = self.p.load()

        self.assertTrue(isinstance(loaded_data, faces.Faces))
        self.assertTrue(isinstance(loaded_data, faces.Faces))

    def test_save_load(self):
        original_data = [1, 2, 3]

        self.p.save(original_data)
        loaded_data = self.p.load()

        self.assertTrue(original_data == loaded_data)

    def tearDown(self):
        # Delete backups between tests
        try:
            os.remove(self.filepath)
        except FileNotFoundError:
            pass
