from __future__ import annotations

import datetime
from typing import Callable

from PyQt6.QtCore import QTime
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)


class IntervalTimerView(QWidget):
    def __init__(self, *, on_close: Callable[[], None]):
        super().__init__()
        self._on_close = on_close

        self.setWindowTitle("Interval Timer")
        self.setMinimumWidth(520)

        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Interval Timer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        settings_box = QGroupBox("Einstellungen")
        settings_layout = QGridLayout(settings_box)

        settings_layout.addWidget(QLabel("Startzeit (HH:MM):"), 0, 0)
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime.currentTime())
        settings_layout.addWidget(self.start_time_edit, 0, 1)

        settings_layout.addWidget(QLabel("Intervall (Minuten):"), 1, 0)
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setMinimum(0.01)
        self.interval_spin.setMaximum(60_000)
        self.interval_spin.setDecimals(2)
        self.interval_spin.setValue(10.0)
        settings_layout.addWidget(self.interval_spin, 1, 1)

        settings_layout.addWidget(QLabel("Anzahl Töne:"), 2, 0)
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(1_000_000)
        self.count_spin.setValue(5)
        settings_layout.addWidget(self.count_spin, 2, 1)

        settings_layout.addWidget(QLabel("Soundfile:"), 3, 0)
        sound_row = QHBoxLayout()
        self.sound_combo = QComboBox()
        self.sound_combo.setMinimumWidth(260)
        sound_row.addWidget(self.sound_combo, 1)
        self.browse_btn = QPushButton("Auswählen …")
        sound_row.addWidget(self.browse_btn)
        settings_layout.addLayout(sound_row, 3, 1)

        layout.addWidget(settings_box)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Starten")
        self.stop_btn = QPushButton("Stoppen")
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)

        status_box = QGroupBox("Status")
        status_layout = QGridLayout(status_box)

        self.countdown_label = QLabel("—")
        countdown_font = QFont()
        countdown_font.setPointSize(22)
        countdown_font.setBold(True)
        self.countdown_label.setFont(countdown_font)
        status_layout.addWidget(self.countdown_label, 0, 0, 1, 2)

        status_layout.addWidget(QLabel("Nächster Ton um:"), 1, 0)
        self.next_time_label = QLabel("—")
        status_layout.addWidget(self.next_time_label, 1, 1)

        status_layout.addWidget(QLabel("Töne verbleibend:"), 2, 0)
        self.remaining_label = QLabel("—")
        status_layout.addWidget(self.remaining_label, 2, 1)

        status_layout.addWidget(QLabel("Status:"), 3, 0)
        self.status_label = QLabel("Bereit")
        status_layout.addWidget(self.status_label, 3, 1)

        layout.addWidget(status_box)

        log_box = QGroupBox("Log")
        log_layout = QVBoxLayout(log_box)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        log_font = QFont("Consolas", 9)
        self.log_text.setFont(log_font)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_box)

    # ── Dialoge / Input ──────────────────────────────────────────────────

    def ask_sound_file(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Tondatei auswählen",
            "",
            "Audio (*.wav *.mp3 *.ogg);;Alle Dateien (*.*)",
        )
        return path

    def show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def get_inputs(self) -> tuple[datetime.time, float, int]:
        t = self.start_time_edit.time()
        start_time = datetime.time(hour=t.hour(), minute=t.minute())
        return start_time, float(self.interval_spin.value()), int(self.count_spin.value())

    # ── Status / Log ─────────────────────────────────────────────────────

    def set_running(self, running: bool) -> None:
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)

    def reset_status(self) -> None:
        self.status_label.setText("Bereit")
        self.countdown_label.setText("—")
        self.next_time_label.setText("—")
        self.remaining_label.setText("—")

    def update_countdown(self, text: str) -> None:
        self.countdown_label.setText(text)

    def update_next_time(self, text: str) -> None:
        self.next_time_label.setText(text)

    def update_remaining(self, text: str) -> None:
        self.remaining_label.setText(text)

    def update_status(self, text: str) -> None:
        self.status_label.setText(text)

    def log(self, msg: str) -> None:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{ts}] {msg}")
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    # ── Close ────────────────────────────────────────────────────────────

    def closeEvent(self, event):  # type: ignore[override]
        self._on_close()
        event.accept()
