from __future__ import annotations

import datetime
import os
import threading
import time

from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from .model import TimerConfig, compute_skipped_intervals, create_default_beep
from .view import IntervalTimerView


class _UiBridge(QObject):
    countdown = pyqtSignal(str)
    next_time = pyqtSignal(str)
    remaining = pyqtSignal(str)
    status = pyqtSignal(str)
    log = pyqtSignal(str)
    running = pyqtSignal(bool)
    play_sound = pyqtSignal(str)


class IntervalTimerController:
    def __init__(self):
        self._default_sound = create_default_beep()
        self.sound_path: str | None = None  # None => default

        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None

        self._ui = _UiBridge()

        self._audio_output = QAudioOutput()
        self._audio_output.setVolume(1.0)
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._player.errorOccurred.connect(self._on_audio_error)  # type: ignore[attr-defined]

        self.view = IntervalTimerView(on_close=self.on_close)

        # Wire UI signals -> view updates
        self._ui.countdown.connect(self.view.update_countdown)
        self._ui.next_time.connect(self.view.update_next_time)
        self._ui.remaining.connect(self.view.update_remaining)
        self._ui.status.connect(self.view.update_status)
        self._ui.log.connect(self.view.log)
        self._ui.running.connect(self.view.set_running)
        self._ui.play_sound.connect(self._play_sound)

        # Wire view controls -> controller
        self.view.start_btn.clicked.connect(self.start)  # type: ignore[arg-type]
        self.view.stop_btn.clicked.connect(self.stop)  # type: ignore[arg-type]
        self.view.browse_btn.clicked.connect(self.browse_sound)  # type: ignore[arg-type]
        self.view.reset_sound_btn.clicked.connect(self.reset_sound)  # type: ignore[arg-type]

        self._set_default_sound_label()

    # ── Sound ─────────────────────────────────────────────────────────────

    def _set_default_sound_label(self) -> None:
        self.view.set_sound_label("Standard-Ton (Beep)")

    def browse_sound(self) -> None:
        path = self.view.ask_sound_file()
        if path:
            self.sound_path = path
            self.view.set_sound_label(os.path.basename(path))
            self.view.log(f"Sound: {os.path.basename(path)}")

    def reset_sound(self) -> None:
        self.sound_path = None
        self._set_default_sound_label()

    def _effective_sound_path(self) -> str:
        return self.sound_path or self._default_sound

    def _play_sound(self, path: str) -> None:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            self._ui.log.emit(f"⚠️ Sound-Datei nicht gefunden: {abs_path}")
            return

        url = QUrl.fromLocalFile(abs_path)
        self._player.setSource(url)
        self._player.play()

    def _on_audio_error(self, *args) -> None:
        # Keep it simple: log Qt's current error string.
        msg = self._player.errorString()
        if msg:
            self._ui.log.emit(f"⚠️ Audio-Fehler: {msg}")

    # ── Eingaben / Validierung ─────────────────────────────────────────────

    def _parse_inputs(self) -> tuple[TimerConfig, int] | None:
        start_time, interval_min, count = self.view.get_inputs()

        now = datetime.datetime.now()
        start_dt = now.replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=0,
            microsecond=0,
        )

        if interval_min <= 0:
            self.view.show_error("Fehler", "Intervall muss eine positive Zahl sein.")
            return None

        if count <= 0:
            self.view.show_error("Fehler", "Anzahl muss eine positive ganze Zahl sein.")
            return None

        interval_sec = float(interval_min) * 60.0
        skipped = compute_skipped_intervals(now=now, start_dt=start_dt, interval_sec=interval_sec)

        return TimerConfig(start_dt=start_dt, interval_sec=interval_sec, count=count), skipped

    # ── Timer-Steuerung ────────────────────────────────────────────────────

    def start(self) -> None:
        parsed = self._parse_inputs()
        if parsed is None:
            return

        config, skipped = parsed

        self._stop_event.clear()
        self._ui.running.emit(True)

        if skipped >= config.count:
            self.view.show_info(
                "Hinweis", "Alle Töne liegen in der Vergangenheit. Startzeit anpassen."
            )
            self._reset_ui()
            return

        self._ui.log.emit(
            f"Start: {config.start_dt:%H:%M}  |  alle {config.interval_sec / 60:.4g} min  |  {config.count}×"
        )
        if skipped:
            self._ui.log.emit(
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
        self._ui.log.emit("⏹ Gestoppt.")

    def _reset_ui(self) -> None:
        self._ui.running.emit(False)
        self._ui.status.emit("Bereit")
        self._ui.countdown.emit("—")
        self._ui.next_time.emit("—")
        self._ui.remaining.emit("—")

    # ── Worker ─────────────────────────────────────────────────────────────

    def _run_worker(self, config: TimerConfig, skipped: int) -> None:
        start_dt = config.start_dt
        interval_sec = config.interval_sec
        count = config.count

        for i in range(skipped + 1, count + 1):
            if self._stop_event.is_set():
                return

            target = start_dt + datetime.timedelta(seconds=i * interval_sec)
            remaining = count - i + 1

            while True:
                if self._stop_event.is_set():
                    return

                diff = (target - datetime.datetime.now()).total_seconds()
                if diff <= 0:
                    break

                mins, secs = divmod(int(diff), 60)
                self._ui.countdown.emit(f"{mins:02d}:{secs:02d}")
                self._ui.next_time.emit(target.strftime("%H:%M:%S"))
                self._ui.remaining.emit(str(remaining))
                self._ui.status.emit(f"Warte auf Ton {i}/{count} …")

                time.sleep(min(0.5, diff))

            if self._stop_event.is_set():
                return

            self._ui.play_sound.emit(self._effective_sound_path())
            now_s = datetime.datetime.now().strftime("%H:%M:%S")
            self._ui.log.emit(f"🔔 Ton {i}/{count} um {now_s}")
            self._ui.status.emit(f"✔ Ton {i}/{count} gespielt")

            if i < count:
                next_t = start_dt + datetime.timedelta(seconds=(i + 1) * interval_sec)
                self._ui.next_time.emit(next_t.strftime("%H:%M:%S"))
                self._ui.remaining.emit(str(count - i))

        if not self._stop_event.is_set():
            self._ui.log.emit("✅ Alle Töne abgespielt.")
            self._ui.countdown.emit("Fertig")
            self._ui.status.emit("✅ Fertig")
            self._ui.running.emit(False)

    # ── Close ──────────────────────────────────────────────────────────────

    def on_close(self) -> None:
        self._stop_event.set()
        try:
            os.unlink(self._default_sound)
        except OSError:
            pass
