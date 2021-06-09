import os
from unittest import TestCase

import tree.backend.constants as constants
import tree.backend.storage.pickle_storage as pickle_storage


class TestStorage(TestCase):
    def setUp(self):
        self.filepath = os.path.join(constants.backup_filepath, constants.pickle_storage_filename)
        self.p = pickle_storage.PickleStorage()

        # Delete pre-existing backups between tests
        try:
            os.remove(self.filepath)
        except FileNotFoundError:
            pass

    def test_load(self):
        loaded_data = self.p.load()

        self.assertTrue(loaded_data == [])

    def test_save_load(self):
        original_data = []

        self.p.save(original_data)
        loaded_data = self.p.load()

        self.assertTrue(original_data == loaded_data)
