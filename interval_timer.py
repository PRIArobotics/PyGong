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

import tkinter as tk

from pygong.controller import IntervalTimerController


# ── Einstiegspunkt ─────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    IntervalTimerController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
