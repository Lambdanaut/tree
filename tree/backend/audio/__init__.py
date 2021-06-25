import abc
import os
import sys
import tempfile

import playsound
import pydub
import sounddevice
import scipy.io.wavfile

sys.path.append('.')

import tree.backend.constants as constants


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

        time_elapsed = 0
        # ongoing_segment = pydub.AudioSegment.silent(
        #     duration=self.max_duration*1000,
        #     frame_rate=self.sample_rate
        # )
        ongoing_segment = None
        while True:
            # Start recording
            recording = sounddevice.rec(int(self.silence_duration * self.sample_rate))

            # Wait until recording is finished
            sounddevice.wait()

            # Write recording to temporary file to be read by pydub
            with tempfile.TemporaryFile() as f:
                scipy.io.wavfile.write(f, self.sample_rate, recording)

                # Load audio segment into pydub for analysis
                segment = pydub.AudioSegment.from_wav(f)

                # Break if the last recording was silent
                is_silent = self._is_silent(segment)
                if is_silent:
                    break

                if ongoing_segment:
                    ongoing_segment = ongoing_segment.append(segment)
                else:
                    ongoing_segment = segment

                print(len(ongoing_segment))

            # Break if the recording is too long
            time_elapsed += self.silence_duration
            if time_elapsed >= self.max_duration:
                break

        # Save as WAV file
        filepath = self._filepath_from_filename(filename)
        ongoing_segment.export(filepath, format="wav")


wa = WavAudio()
wa.record("test.wav")
wa.play("test.wav")
