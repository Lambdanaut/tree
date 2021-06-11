import abc


class Storage(abc.ABC):
    @abc.abstractmethod
    def save(self, data):
        pass

    @abc.abstractmethod
    def load(self):
        pass
