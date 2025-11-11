import logging
import struct
from dataclasses import dataclass
from typing import Optional

import speech_recognition as sr


logger = logging.getLogger(__name__)


@dataclass
class WakeWordDetectionResult:
    """Represents the outcome of a wake-word detection."""

    command_text: Optional[str] = None

    @property
    def requires_follow_up_recording(self) -> bool:
        return self.command_text is None


class BaseWakeWordDetector:
    """Base class for wake-word detectors."""

    def wait_for_activation(self) -> WakeWordDetectionResult:  # pragma: no cover - interface
        raise NotImplementedError


class PorcupineWakeWordDetector(BaseWakeWordDetector):
    """Wake-word detector powered by pvporcupine."""

    def __init__(self, keyword_path: str, sensitivity: float = 0.5, device_index: Optional[int] = None):
        try:
            import pvporcupine
            import pyaudio
        except ImportError as exc:  # pragma: no cover - defensive
            raise RuntimeError("pvporcupine is required for the Porcupine wake-word detector") from exc

        self._pvporcupine = pvporcupine.create(keyword_paths=[keyword_path], sensitivities=[sensitivity])
        self._pyaudio = pyaudio.PyAudio()
        self._device_index = device_index
        self._stream = None

    def _open_stream(self):
        import pyaudio

        if self._stream is None:
            self._stream = self._pyaudio.open(
                rate=self._pvporcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self._pvporcupine.frame_length,
                input_device_index=self._device_index,
            )

    def wait_for_activation(self) -> WakeWordDetectionResult:
        self._open_stream()
        logger.info("Listening for wake word with Porcupine detector…")

        while True:
            pcm = self._stream.read(self._pvporcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * self._pvporcupine.frame_length, pcm)
            if self._pvporcupine.process(pcm_unpacked) >= 0:
                logger.info("Wake word detected by Porcupine.")
                return WakeWordDetectionResult()

    def close(self):  # pragma: no cover - resource cleanup
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._pyaudio is not None:
            self._pyaudio.terminate()


class SpeechRecognitionWakeWordDetector(BaseWakeWordDetector):
    """Fallback detector relying on speech recognition for keyword spotting."""

    def __init__(
        self,
        recognizer: sr.Recognizer,
        assistant_name: str,
        language: str = "fr-FR",
        listen_timeout: float = 3.0,
        device_index: Optional[int] = None,
    ):
        self._recognizer = recognizer
        self._assistant_name = assistant_name.lower()
        self._language = language
        self._listen_timeout = listen_timeout
        self._device_index = device_index

    def wait_for_activation(self) -> WakeWordDetectionResult:
        logger.info("Listening for wake word with speech recognition fallback…")

        while True:
            with sr.Microphone(device_index=self._device_index) as source:
                audio = self._recognizer.listen(source, timeout=None, phrase_time_limit=self._listen_timeout)

            try:
                transcription = self._recognizer.recognize_google(audio, language=self._language)
                logger.debug("Wake-word fallback transcription: %s", transcription)
            except sr.UnknownValueError:
                logger.debug("Wake-word fallback could not understand audio.")
                continue
            except sr.RequestError as error:  # pragma: no cover - network failure
                logger.error("Wake-word fallback request error: %s", error)
                continue

            normalized = transcription.lower()
            if self._assistant_name in normalized:
                logger.info("Wake word detected through fallback recognizer.")
                remainder = normalized.replace(self._assistant_name, "", 1).strip()
                if remainder:
                    return WakeWordDetectionResult(command_text=transcription)
                return WakeWordDetectionResult()


class WakeWordDetector:
    """Facade that selects the best wake-word strategy based on configuration."""

    def __init__(self, configuration):
        self._configuration = configuration

    def wait_for_activation(
        self,
        recognizer: sr.Recognizer,
        language: str = "fr-FR",
        device_index: Optional[int] = None,
    ) -> WakeWordDetectionResult:
        wake_word_configuration = self._configuration.get("wake_word", {})

        keyword_path = wake_word_configuration.get("porcupine_keyword_path")
        sensitivity = wake_word_configuration.get("porcupine_sensitivity", 0.6)

        if keyword_path:
            try:
                detector = PorcupineWakeWordDetector(
                    keyword_path=keyword_path,
                    sensitivity=sensitivity,
                    device_index=device_index,
                )
                try:
                    return detector.wait_for_activation()
                finally:
                    detector.close()
            except RuntimeError:
                logger.warning(
                    "pvporcupine is not available. Falling back to speech-recognition-based wake-word detection.",
                )

        fallback_timeout = wake_word_configuration.get("fallback_listen_timeout", 3.0)
        detector = SpeechRecognitionWakeWordDetector(
            recognizer=recognizer,
            assistant_name=self._configuration.get("assistant_name", ""),
            language=language,
            listen_timeout=fallback_timeout,
            device_index=device_index,
        )
        return detector.wait_for_activation()
