from __future__ import annotations

from dataclasses import dataclass
import datetime
import math
import os
import struct
import tempfile
import wave


def create_default_beep(
    freq: float = 880.0,
    duration: float = 0.6,
    sample_rate: int = 44100,
    *,
    beeps: int = 3,
    gap: float = 0.08,
) -> str:
    """Generiert einen Alarm-Beep (mehrere kurze Piepser) als temporäre WAV-Datei.

    Standard: 3 Piepser mit kurzen Pausen ("Alarm").
    - duration: Gesamtdauer der erzeugten WAV-Datei (in Sekunden)
    - beeps: Anzahl der Piepser innerhalb der Gesamtdauer
    - gap: Pause zwischen den Piepsern (in Sekunden)
    """

    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")

    beeps = max(1, int(beeps))
    duration = max(0.0, float(duration))
    gap = max(0.0, float(gap))

    total_samples = max(beeps, int(sample_rate * duration))

    gap_samples = 0 if beeps == 1 else int(sample_rate * gap)
    gap_samples = max(0, gap_samples)

    if beeps > 1:
        # Ensure we always have at least 1 sample per beep; shrink the gap if needed.
        max_gap_samples = max(0, (total_samples - beeps) // (beeps - 1))
        gap_samples = min(gap_samples, max_gap_samples)

    remaining_for_beeps = total_samples - (beeps - 1) * gap_samples
    beep_samples = max(1, remaining_for_beeps // beeps)
    trailing_silence_samples = total_samples - (
        beeps * beep_samples + (beeps - 1) * gap_samples
    )

    # Fade to avoid clicks; keep it short so it also works for short beeps.
    fade_samples = min(int(sample_rate * 0.02), beep_samples // 2)  # up to 20ms

    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)

        for beep_idx in range(beeps):
            for i in range(beep_samples):
                env = 1.0
                if fade_samples:
                    if i < fade_samples:
                        env = i / fade_samples
                    elif i >= beep_samples - fade_samples:
                        env = (beep_samples - i) / fade_samples

                val = int(32767 * env * math.sin(2 * math.pi * freq * i / sample_rate))
                f.writeframes(struct.pack("<h", val))

            if beep_idx < beeps - 1:
                for _ in range(gap_samples):
                    f.writeframes(struct.pack("<h", 0))

        for _ in range(trailing_silence_samples):
            f.writeframes(struct.pack("<h", 0))

    return path


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
