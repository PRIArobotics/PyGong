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

        # Initialize multimedia lazily on first playback. On some Linux systems,
        # early multimedia init can block before the main window is shown.
        self._audio_output: QAudioOutput | None = None
        self._player: QMediaPlayer | None = None

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
        self.view.sound_combo.currentIndexChanged.connect(self.on_sound_selected)  # type: ignore[arg-type]

        self._load_gongs()

    # ── Sound ─────────────────────────────────────────────────────────────

    def _load_gongs(self) -> None:
        """Load gongs from the gongs folder and populate the dropdown."""
        gongs_dir = self._get_gongs_dir()
        
        # Block signals during initialization to avoid multiple triggers
        self.view.sound_combo.blockSignals(True)
        
        # Add default beep as first option
        self.view.sound_combo.addItem("Standard-Ton (Beep)", None)
        
        # Scan gongs directory for audio files
        audio_extensions = {'.wav', '.mp3', '.ogg', '.flac', '.m4a'}
        
        if os.path.isdir(gongs_dir):
            try:
                files = sorted(os.listdir(gongs_dir))
                for filename in files:
                    file_path = os.path.join(gongs_dir, filename)
                    if os.path.isfile(file_path):
                        _, ext = os.path.splitext(filename.lower())
                        if ext in audio_extensions:
                            self.view.sound_combo.addItem(filename, file_path)
            except (OSError, PermissionError) as e:
                self.view.log(f"⚠️ Fehler beim Laden der Gongs: {e}")
        
        # Unblock signals and set initial selection
        self.view.sound_combo.blockSignals(False)
        self.view.sound_combo.setCurrentIndex(0)  # Select default beep
        self.sound_path = None  # Ensure sound_path is None for default

    def _get_gongs_dir(self) -> str:
        """Get the gongs directory path."""
        return "gongs"

    def on_sound_selected(self, index: int) -> None:
        """Handle when a gong is selected from the dropdown."""
        self.sound_path = self.view.sound_combo.itemData(index)
        selected_name = self.view.sound_combo.itemText(index)
        self.view.log(f"🎵 Gong ausgewählt: {selected_name}")

    def browse_sound(self) -> None:
        """Open file dialog to browse for a custom sound file."""
        path = self.view.ask_sound_file()
        if path:
            # Add to dropdown and select it
            filename = os.path.basename(path)
            # Check if already in combo
            index = self.view.sound_combo.findData(path)
            if index == -1:
                # Add new entry
                self.view.sound_combo.addItem(filename, path)
                index = self.view.sound_combo.count() - 1
            self.view.sound_combo.setCurrentIndex(index)
            self.view.log(f"🎵 Datei ausgewählt: {filename}")

    def _effective_sound_path(self) -> str:
        return self.sound_path or self._default_sound

    def _ensure_audio_player(self) -> bool:
        if self._player is not None and self._audio_output is not None:
            return True

        try:
            self._audio_output = QAudioOutput()
            self._audio_output.setVolume(1.0)
            self._player = QMediaPlayer()
            self._player.setAudioOutput(self._audio_output)
            self._player.errorOccurred.connect(self._on_audio_error)  # type: ignore[attr-defined]
            return True
        except Exception as exc:
            self._ui.log.emit(f"⚠️ Audio-Initialisierung fehlgeschlagen: {exc}")
            self._audio_output = None
            self._player = None
            return False

    def _play_sound(self, path: str) -> None:
        if not self._ensure_audio_player() or self._player is None:
            return

        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            self._ui.log.emit(f"⚠️ Sound-Datei nicht gefunden: {abs_path}")
            return

        url = QUrl.fromLocalFile(abs_path)
        self._player.setSource(url)
        # Give the player a moment to prepare
        time.sleep(0.05)
        self._player.play()
        self._ui.log.emit(f"🔊 Spiele: {abs_path}")

    def _on_audio_error(self, *args) -> None:
        # Keep it simple: log Qt's current error string.
        if self._player is None:
            return

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

            # Verwende den aktuellen Sound-Pfad (kann während Laufzeit geändert worden sein)
            current_sound = self._effective_sound_path()
            self._ui.play_sound.emit(current_sound)
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
