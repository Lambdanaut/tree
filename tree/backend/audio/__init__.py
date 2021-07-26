from array import array
import abc
import os
from queue import Queue, Full
import sys
import threading

import pyaudio
import playsound
import sounddevice
import wave

sys.path.append('.')

import tree.backend.constants as constants


p = pyaudio.PyAudio()


class NoAudioHeardException(Exception):
    """Raised if we couldn't record any audio"""
    pass


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
    channels = 1  # 1 for mono, 2 for stereo
    chunk_size = 1024
    buf_max_size = chunk_size * 10  # if the recording thread can't consume fast enough, the listener will start discarding
    format = pyaudio.paInt16

    def __init__(
            self,
            max_duration: int = 12,
            silence_threshold: int = 90,  # Anything below this volume is considered silent
            silence_duration: float = 0.75,  # Number of seconds to look back on to count silence duration
            filepath: str = None):

        """
        Usage:
            wa = WavAudio()
            wa.calibrate()  # Calibrates the silence threshold
            wa.record("test.wav")  # Records a segment of audio until silence is heard
            wa.play("test.wav")


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

    def _is_silent(self, frames: list) -> bool:
        for frame in frames:
            volume = max(frame)
            if volume > self.silence_threshold:
                return False
        return True

    def print_chunk_volume(self, chunk: list):
        vol = max(chunk)
        print('█' * int(vol / 100))

    def calibrate(self, play_demo_audio: bool = True):
        """
        Sets the silence_threshold after a calibration period of detected silence.
        """
        # Play calibration beginning audio
        if play_demo_audio:
            print("Calibration process started")
            print("===========================")

            calibration1_filepath = os.path.join(constants.static_filepath, 'calibration1.wav')
            playsound.playsound(calibration1_filepath)

            print(" - Remain silent for 4 seconds")

        frame_volumes = []  # Initialize list to store frames

        # Store data in chunks for 4 seconds
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.sample_rate,
                        frames_per_buffer=self.chunk_size,
                        input=True)
        for i in range(0, int(self.sample_rate / self.chunk_size * 4)):
            volume = max(stream.read(self.chunk_size))
            frame_volumes.append(volume)

        avg = sum(frame_volumes) / len(frame_volumes)
        calibrated_value = int(avg*1.5)  # A bit noisier than the average

        self.silence_threshold = calibrated_value

        # Play calibration complete audio
        if play_demo_audio:
            calibration2_filepath = os.path.join(constants.static_filepath, 'calibration2.wav')
            playsound.playsound(calibration2_filepath)

            print("Calibration process complete!")
            print("Calibrated silence threshold set to `{}`".format(self.silence_threshold))

        return calibrated_value

    def play(self, filename: str):
        filepath = self._filepath_from_filename(filename)
        playsound.playsound(filepath)

    def record(self, filename: str):
        # Documentation for sounddevice:
        # https://python-sounddevice.readthedocs.io/en/latest/usage.html

        def _record_to_file(stopped, q):
            duration_so_far: float = 0.0
            has_recorded_nonsilence_yet: bool = False
            frames: list = []

            while True:
                if stopped.wait(timeout=0):
                    # End this thread if we get a stop event
                    break

                # Keep track of how many chunks of time we've processed
                duration_so_far += self.silence_duration

                # Read the chunks from the queue until we have an audio that is self.silence_duration in length
                frames_to_inspect = []
                for i in range(0, int(self.sample_rate / self.chunk_size * self.silence_duration)):
                    frame = q.get()

                    self.print_chunk_volume(frame)  # Debug print chunk volume

                    frames_to_inspect.append(frame)

                frames += frames_to_inspect
                is_silent = self._is_silent(frames_to_inspect)
                if is_silent:
                    if has_recorded_nonsilence_yet:
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

                        print("killed")
                        sys.exit()
                    elif duration_so_far > self.silence_duration * 20:
                        # Raised if no audio was ever recorded for 20 times the length of a silence duration
                        raise NoAudioHeardException
                else:
                    has_recorded_nonsilence_yet = True

        def _listen(stopped, q):
            stream = pyaudio.PyAudio().open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            while True:
                if stopped.wait(timeout=0):
                    break
                try:
                    q.put(array('h', stream.read(self.chunk_size)))
                except Full:
                    pass  # discard

        stopped_event = threading.Event()
        q = Queue(maxsize=int(round(self.buf_max_size / self.chunk_size)))

        listen_t = threading.Thread(target=_listen, args=(stopped_event, q))
        listen_t.start()
        record_t = threading.Thread(target=_record_to_file, args=(stopped_event, q))
        record_t.start()

        try:
            while True:
                listen_t.join(0.1)
                record_t.join(0.1)
        except KeyboardInterrupt:
            stopped_event.set()

        listen_t.join()
        record_t.join()


if __name__ == '__main__':
    # Run demo
    wa = WavAudio()
    wa.calibrate()  # Calibrates the silence threshold
    wa.record("test.wav")  # Records a segment of audio until silence is heard
    wa.play("test.wav")
