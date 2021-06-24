import abc
import os
import sys

import playsound
import sounddevice
from scipy.io.wavfile import write

sys.path.append('.')

import tree.backend.constants as constants


class Audio(abc.ABC):
    @abc.abstractmethod
    def play(self, filepath: str):
        pass

    @abc.abstractmethod
    def record(self, filepath: str, duration: float):
        """
        Records audio for `duration` seconds and saves it to `filepath`

        :param filepath: Filepath to save recording
        :param duration: Duration in seconds
        :return:
        """
        pass


class WavAudio(Audio):
    sample_rate = 44100

    def __init__(self, filepath: str = None):
        # Initialize sample rate and channels for all recordings
        sounddevice.default.samplerate = self.sample_rate
        sounddevice.default.channels = 2

        self.filepath = filepath or constants.audio_recordings_filepath

    def _filepath_from_filename(self, filename: str):
        return os.path.join(self.filepath, filename)

    def play(self, filename: str):
        playsound.playsound(self._filepath_from_filename(filename))

    def record(self, filename: str, duration: float):
        # Documentation for sounddevice:
        # https://python-sounddevice.readthedocs.io/en/latest/usage.html

        # Start recording
        recording = sounddevice.rec(int(duration * self.sample_rate))

        # Wait until recording is finished
        sounddevice.wait()

        # Save as WAV file
        filepath = self._filepath_from_filename(filename)
        write(filepath, self.sample_rate, recording)
