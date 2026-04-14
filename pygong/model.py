from __future__ import annotations

from dataclasses import dataclass
import datetime
import math
import os
import struct
import tempfile
import wave

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect

_SFX = QSoundEffect()
_SFX.setVolume(1.0)


def create_default_beep(
    freq: float = 880.0,
    duration: float = 0.6,
    sample_rate: int = 44100,
) -> str:
    """Generiert einen einfachen Sinus-Beep als temporäre WAV-Datei."""
    n = int(sample_rate * duration)
    fade = int(sample_rate * 0.04)  # 40ms fade in/out

    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(n):
            env = 1.0
            if i < fade:
                env = i / fade
            elif i > n - fade:
                env = (n - i) / fade
            val = int(32767 * env * math.sin(2 * math.pi * freq * i / sample_rate))
            f.writeframes(struct.pack("<h", val))

    return path


def play_sound(path: str) -> None:
    """Spielt eine WAV-Datei asynchron ab (QtMultimedia)."""
    # QSoundEffect unterstützt WAV zuverlässig; andere Formate hängen von Plattform/Codecs ab.
    _SFX.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
    _SFX.play()


@dataclass(frozen=True)
class TimerConfig:
    start_dt: datetime.datetime
    interval_sec: float
    count: int


def compute_skipped_intervals(
    *,
    now: datetime.datetime,
    start_dt: datetime.datetime,
    interval_sec: float,
) -> int:
    """Wie viele Intervalle seit start_dt bereits vergangen sind (>= 0)."""
    elapsed = (now - start_dt).total_seconds()
    if elapsed <= 0 or interval_sec <= 0:
        return 0
    return max(0, int(elapsed / interval_sec))
