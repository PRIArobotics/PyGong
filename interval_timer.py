#!/usr/bin/env python3
"""
Interval Timer
Spielt ab einer Startzeit alle N Minuten einen Ton ab – auch wenn die Startzeit in der Vergangenheit liegt.
Abhängigkeiten: pip install -r requirements.txt

MVC-Aufteilung:
- Model: pygong/model.py
- View: pygong/view.py
- Controller: pygong/controller.py
"""

import os
import sys


def _setup_qt_plugin_path_for_frozen() -> None:
    """Ensure Qt platform plugins can be found in bundled executables."""
    if not (hasattr(sys, "frozen") and sys.platform in ("linux", "darwin")):
        return

    base_dir = os.path.dirname(sys.executable)
    meipass = getattr(sys, "_MEIPASS", "")

    possible_plugin_paths = [
        os.path.join(base_dir, "PyQt6", "plugins"),
        os.path.join(base_dir, "..", "_internal", "PyQt6", "plugins"),
        os.path.join(base_dir, "lib", "PyQt6", "plugins"),
    ]

    if meipass:
        possible_plugin_paths.extend(
            [
                os.path.join(meipass, "PyQt6", "Qt6", "plugins"),
                os.path.join(meipass, "PyQt6", "plugins"),
                os.path.join(meipass, "qt6_plugins"),
            ]
        )

    for plugins_dir in possible_plugin_paths:
        if os.path.isdir(plugins_dir):
            os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", plugins_dir)
            break


def _ensure_linux_gui_environment() -> None:
    """Fail fast with a clear error if no Linux GUI session is available."""
    if sys.platform != "linux":
        return

    platform = os.environ.get("QT_QPA_PLATFORM", "").strip().lower()
    if platform in {"offscreen", "minimal"}:
        return

    has_x11 = bool(os.environ.get("DISPLAY"))
    has_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
    if has_x11 or has_wayland:
        return

    print(
        "[PyGong] Kein grafisches Linux-Display erkannt (DISPLAY/WAYLAND_DISPLAY fehlt).\n"
        "Bitte in einer Desktop-Sitzung starten oder DISPLAY korrekt setzen.",
        file=sys.stderr,
        flush=True,
    )
    raise SystemExit(2)


# Ensure Qt platform plugins can be found in bundled executables (Linux/macOS)
_setup_qt_plugin_path_for_frozen()

from PyQt6.QtWidgets import QApplication

from pygong.controller import IntervalTimerController


# ── Einstiegspunkt ─────────────────────────────────────────────────────────────

def main():
    _ensure_linux_gui_environment()

    app = QApplication(sys.argv)
    controller = IntervalTimerController()
    controller.view.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
