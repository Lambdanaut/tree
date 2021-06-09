import tree.backend.storage.pickle_storage as pickle_storage


class Face(object):
    def __init__(self, encoding):
        self.encoding = encoding
        self.messages = []


class Faces(object):
    def __init__(self, faces=None):
        self.faces = faces or []

    @property
    def face_encodings(self):
        return (face.encoding for face in self.faces)

    def save(self):
        return self.pickle_storage.save(self)

    def add_face(self):
        pass
