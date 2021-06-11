import pickle
import os
import sys
from typing import Union

sys.path.append('.')

import tree.backend.constants as constants
import tree.backend.faces as faces
import tree.backend.storage as storage


class PickleStorage(storage.Storage):

    def __init__(self, filename: Union[str, None] = None):
        self.filename = filename or constants.pickle_storage_filename
        self.backup_filepath = os.path.join(constants.backup_filepath, self.filename)

    def save(self, data: "faces.Faces"):
        with open(self.backup_filepath, 'wb') as backup_file:
            pickle.dump(data, backup_file)

    def load(self):
        try:
            with open(self.backup_filepath, 'rb') as backup_file:
                data = pickle.load(backup_file)
                return data

        except FileNotFoundError:
            self.save(faces.Faces())

        # If nothing to load, return a fresh empty faces object
        return faces.Faces()


pickle_storage = PickleStorage()
