from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WakeWordConfig:
    access_key: str
    keyword_path: str
    model_path: str | None = None


class PorcupineWakeWord:
    def __init__(self, config: WakeWordConfig) -> None:
        try:
            import pvporcupine
            from pvrecorder import PvRecorder
        except ImportError as exc:
            raise RuntimeError(
                "Install Raspberry Pi wake-word dependencies with: pip install -e '.[pi]'"
            ) from exc

        self._pvrecorder_cls = PvRecorder
        args = {
            "access_key": config.access_key,
            "keyword_paths": [config.keyword_path],
        }
        if config.model_path:
            args["model_path"] = config.model_path
        self._porcupine = pvporcupine.create(**args)
        self._recorder = PvRecorder(device_index=-1, frame_length=self._porcupine.frame_length)

    def wait(self) -> None:
        self._recorder.start()
        try:
            while True:
                pcm = self._recorder.read()
                if self._porcupine.process(pcm) >= 0:
                    return
        finally:
            self._recorder.stop()

    def close(self) -> None:
        self._recorder.delete()
        self._porcupine.delete()
