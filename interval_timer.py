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

# Ensure Qt platform plugins can be found in bundled executables (Linux/macOS)
if hasattr(sys, 'frozen') and sys.platform in ('linux', 'darwin'):
    base_dir = os.path.dirname(sys.executable)
    
    # Try multiple possible plugin paths
    possible_plugin_paths = [
        os.path.join(base_dir, 'PyQt6', 'plugins'),  # Direct path
        os.path.join(base_dir, '..', '_internal', 'PyQt6', 'plugins'),  # PyInstaller internal
        os.path.join(base_dir, 'lib', 'PyQt6', 'plugins'),  # Alternative structure
    ]
    
    for plugins_dir in possible_plugin_paths:
        if os.path.isdir(plugins_dir):
            os.environ.setdefault('QT_QPA_PLATFORM_PLUGIN_PATH', plugins_dir)
            break

from PyQt6.QtWidgets import QApplication

from pygong.controller import IntervalTimerController


# ── Einstiegspunkt ─────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    controller = IntervalTimerController()
    controller.view.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
