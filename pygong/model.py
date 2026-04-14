from __future__ import annotations

from dataclasses import dataclass
import datetime
import math
import os
import struct
import sys
import tempfile
import wave

AUDIO_BACKEND: str | None = None


def _init_audio_backend() -> str | None:
    """Initialisiert das Audio-Backend (optional) und gibt dessen Namen zurück."""
    global AUDIO_BACKEND

    if AUDIO_BACKEND is not None:
        return AUDIO_BACKEND

    try:
        import pygame  # type: ignore

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()
        AUDIO_BACKEND = "pygame"
        return AUDIO_BACKEND
    except Exception:
        pass

    if sys.platform == "win32":
        try:
            import winsound  # noqa: F401

            AUDIO_BACKEND = "winsound"
            return AUDIO_BACKEND
        except ImportError:
            pass

    AUDIO_BACKEND = None
    return AUDIO_BACKEND


# Backward-compatible: Backend wie zuvor beim Import initialisieren.
AUDIO_BACKEND = _init_audio_backend()


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
    """Spielt eine WAV/MP3/OGG-Datei asynchron ab."""
    if AUDIO_BACKEND == "pygame":
        try:
            import pygame  # type: ignore

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[Audio-Fehler] {e}", file=sys.stderr)
    elif AUDIO_BACKEND == "winsound":
        try:
            import winsound

            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"[Audio-Fehler] {e}", file=sys.stderr)
    else:
        # Fallback: Terminal-Bell (wenn verfügbar)
        sys.stdout.write("\a")
        sys.stdout.flush()


@dataclass(frozen=True)
class TimerConfig:
    start_dt: datetime.datetime
    interval_sec: float
    count: int
    sound_path: str


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
