from __future__ import annotations

import datetime
import os
import threading
import time

import tkinter as tk

from .model import AUDIO_BACKEND, TimerConfig, compute_skipped_intervals, create_default_beep, play_sound
from .view import IntervalTimerView


class IntervalTimerController:
    def __init__(self, root: tk.Tk):
        self.root = root

        self._default_sound = create_default_beep()
        self.sound_path = self._default_sound

        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None

        self.view = IntervalTimerView(
            root,
            audio_backend=AUDIO_BACKEND,
            on_start=self.start,
            on_stop=self.stop,
            on_browse_sound=self.browse_sound,
            on_reset_sound=self.reset_sound,
            on_close=self.on_close,
        )

        self.view.set_sound(self.sound_path, "Standard-Ton (Beep)")

        if AUDIO_BACKEND is None:
            self.view.log("⚠  Kein Audio-Backend gefunden. Bitte 'pip install pygame' ausführen.")

    # ── Sound ──────────────────────────────────────────────────────────────

    def browse_sound(self) -> None:
        path = self.view.ask_sound_file()
        if path:
            self.sound_path = path
            self.view.set_sound(path, os.path.basename(path))
            self.view.log(f"Sound: {os.path.basename(path)}")

    def reset_sound(self) -> None:
        self.sound_path = self._default_sound
        self.view.set_sound(self.sound_path, "Standard-Ton (Beep)")

    # ── Eingaben / Validierung ─────────────────────────────────────────────

    def _parse_inputs(self) -> tuple[TimerConfig, int] | None:
        """Gibt (config, skipped) zurück oder None bei Fehler."""
        raw_time, raw_interval, raw_count = self.view.get_raw_inputs()

        try:
            t = datetime.datetime.strptime(raw_time, "%H:%M")
        except ValueError:
            self.view.show_error("Fehler", "Startzeit muss im Format HH:MM sein.")
            return None

        now = datetime.datetime.now()
        start_dt = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)

        try:
            interval_min = float(raw_interval.replace(",", "."))
            if interval_min <= 0:
                raise ValueError
        except ValueError:
            self.view.show_error("Fehler", "Intervall muss eine positive Zahl sein.")
            return None

        try:
            count = int(raw_count)
            if count <= 0:
                raise ValueError
        except ValueError:
            self.view.show_error("Fehler", "Anzahl muss eine positive ganze Zahl sein.")
            return None

        interval_sec = interval_min * 60
        skipped = compute_skipped_intervals(now=now, start_dt=start_dt, interval_sec=interval_sec)

        return (
            TimerConfig(
                start_dt=start_dt,
                interval_sec=interval_sec,
                count=count,
                sound_path=self.sound_path,
            ),
            skipped,
        )

    # ── Timer-Steuerung ────────────────────────────────────────────────────

    def start(self) -> None:
        parsed = self._parse_inputs()
        if parsed is None:
            return

        config, skipped = parsed

        self._stop_event.clear()
        self.view.set_running(True)

        if skipped >= config.count:
            self.view.show_info(
                "Hinweis", "Alle Töne liegen in der Vergangenheit. Startzeit anpassen."
            )
            self._reset_ui()
            return

        self.view.log(
            f"Start: {config.start_dt:%H:%M}  |  alle {config.interval_sec / 60:.4g} min  |  {config.count}×"
        )
        if skipped:
            self.view.log(
                f"↪ {skipped} Intervall(e) bereits vergangen – setze bei #{skipped + 1} fort."
            )

        self._worker = threading.Thread(
            target=self._run_worker,
            args=(config, skipped),
            daemon=True,
        )
        self._worker.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._reset_ui()
        self.view.log("⏹ Gestoppt.")

    def _reset_ui(self) -> None:
        self.view.set_running(False)
        self.view.reset_status()

    # ── Worker ─────────────────────────────────────────────────────────────

    def _run_worker(self, config: TimerConfig, skipped: int) -> None:
        """Timer-Thread: berechnet feste Zeitpunkte relativ zur Startzeit."""
        start_dt = config.start_dt
        interval_sec = config.interval_sec
        count = config.count

        for i in range(skipped + 1, count + 1):
            if self._stop_event.is_set():
                return

            target = start_dt + datetime.timedelta(seconds=i * interval_sec)
            remaining = count - i + 1

            # Warte-Loop mit UI-Update alle 0,5 s
            while True:
                if self._stop_event.is_set():
                    return

                diff = (target - datetime.datetime.now()).total_seconds()
                if diff <= 0:
                    break

                mins, secs = divmod(int(diff), 60)
                self.view.call_in_ui_thread(self.view.update_countdown, f"{mins:02d}:{secs:02d}")
                self.view.call_in_ui_thread(self.view.update_next_time, target.strftime("%H:%M:%S"))
                self.view.call_in_ui_thread(self.view.update_remaining, str(remaining))
                self.view.call_in_ui_thread(
                    self.view.update_status,
                    f"Warte auf Ton {i}/{count} …",
                )

                time.sleep(min(0.5, diff))

            if self._stop_event.is_set():
                return

            play_sound(config.sound_path)
            now_s = datetime.datetime.now().strftime("%H:%M:%S")
            self.view.call_in_ui_thread(self.view.log, f"🔔 Ton {i}/{count} um {now_s}")
            self.view.call_in_ui_thread(self.view.update_status, f"✔ Ton {i}/{count} gespielt")

            if i < count:
                next_t = start_dt + datetime.timedelta(seconds=(i + 1) * interval_sec)
                self.view.call_in_ui_thread(self.view.update_next_time, next_t.strftime("%H:%M:%S"))
                self.view.call_in_ui_thread(self.view.update_remaining, str(count - i))

        if not self._stop_event.is_set():
            self.view.call_in_ui_thread(self.view.log, "✅ Alle Töne abgespielt.")
            self.view.call_in_ui_thread(self.view.update_countdown, "Fertig")
            self.view.call_in_ui_thread(self.view.update_status, "✅ Fertig")
            self.view.call_in_ui_thread(self.view.set_running, False)

    # ── Close ──────────────────────────────────────────────────────────────

    def on_close(self) -> None:
        self._stop_event.set()
        try:
            os.unlink(self._default_sound)
        except OSError:
            pass
        self.root.destroy()
