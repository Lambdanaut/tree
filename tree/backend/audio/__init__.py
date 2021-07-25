from array import array
import abc
from collections import deque
import os
from queue import Queue, Full
import sys
import threading

import pyaudio
import playsound
import pydub
import sounddevice
import wave

sys.path.append('.')

import tree.backend.constants as constants


CHUNK_SIZE = 1024
MIN_VOLUME = 500
# if the recording thread can't consume fast enough, the listener will start discarding
BUF_MAX_SIZE = CHUNK_SIZE * 10

p = pyaudio.PyAudio()


class Audio(abc.ABC):
    @abc.abstractmethod
    def play(self, filepath: str):
        pass

    @abc.abstractmethod
    def record(self, filepath: str):
        """
        Records audio for `duration` seconds and saves it to `filepath`

        :param filepath: Filepath to save recording
        :param duration: Duration in seconds
        :return:
        """
        pass


class WavAudio(Audio):
    sample_rate = 44100
    channels = 2
    format = pyaudio.paInt16

    def __init__(
            self,
            max_duration: int = 12,
            silence_threshold: int = -32,
            silence_duration: int = 3,
            filepath: str = None):

        """
        :param max_duration: Maximum length of a complete recording. Will cut early if silence is detected
        :param silence_threshold: The upper bound for how quiet is silent in dFBS
        -32 is a pretty good default for recording speech.
        :param silence_duration: How long to record over and over, detecting silences
        :param filepath: optional filepath to save the final recording to
                         (defaults to constants.audio_recordings_filepath)
        """

        self.max_duration = max_duration
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.filepath = filepath or constants.audio_recordings_filepath

        # Initialize sample rate and channels for all recordings
        sounddevice.default.samplerate = self.sample_rate
        sounddevice.default.channels = self.channels

    def _filepath_from_filename(self, filename: str) -> str:
        return os.path.join(self.filepath, filename)

    def _is_silent(self, segment: pydub.AudioSegment) -> bool:
        silences = pydub.silence.detect_silence(
            segment,
            min_silence_len=self.silence_duration*1000,
            silence_thresh=self.silence_threshold,
            seek_step=1
        )

        return len(silences) >= 1

    def play(self, filename: str):
        filepath = self._filepath_from_filename(filename)
        playsound.playsound(filepath)

    def record(self, filename: str):
        # Documentation for sounddevice:
        # https://python-sounddevice.readthedocs.io/en/latest/usage.html

        def _record(stopped, q):
            frames = []
            while True:
                if stopped.wait(timeout=0):
                    break
                chunk = q.get()
                vol = max(chunk)
                print('█' * int(vol / 100))

                frames.append(chunk)

                if vol < 5:
                    # Save as WAV file
                    filepath = self._filepath_from_filename(filename)

                    # open the file in 'write bytes' mode
                    wf = wave.open(filepath, "wb")
                    # set the channels
                    wf.setnchannels(self.channels)
                    # set the sample format
                    wf.setsampwidth(p.get_sample_size(self.format))
                    # set the sample rate
                    wf.setframerate(self.sample_rate)
                    # write the frames as bytes
                    wf.writeframes(b"".join(frames))
                    # close the file
                    wf.close()

                    sys.exit()

        def _listen(stopped, q):
            stream = pyaudio.PyAudio().open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024,
            )

            while True:
                if stopped.wait(timeout=0):
                    break
                try:
                    q.put(array('h', stream.read(CHUNK_SIZE)))
                except Full:
                    pass  # discard

        stopped = threading.Event()
        q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

        listen_t = threading.Thread(target=_listen, args=(stopped, q))
        listen_t.start()
        record_t = threading.Thread(target=_record, args=(stopped, q))
        record_t.start()

        try:
            while True:
                listen_t.join(0.1)
                record_t.join(0.1)
        except KeyboardInterrupt:
            stopped.set()

        listen_t.join()
        record_t.join()



wa = WavAudio()
wa.record("test.wav")
wa.play("test.wav")
