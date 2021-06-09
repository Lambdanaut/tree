import pickle
import os

import tree.backend.constants as constants
import tree.backend.storage as storage


class PickleStorage(storage.Storage):
    backup_filepath = os.path.join(constants.backup_filepath, constants.pickle_storage_filename)

    def save(self, data):
        with open(self.backup_filepath, 'wb') as backup_file:
            pickle.dump(data, backup_file)

    def load(self):
        try:
            with open(self.backup_filepath, 'rb') as backup_file:
                data = pickle.load(backup_file)
                return data

        except FileNotFoundError:
            self.save([])

        return []


pickle_storage = PickleStorage()