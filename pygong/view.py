from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable

# ── Farben & Fonts ─────────────────────────────────────────────────────────────

BG = "#1a1a2e"
SURFACE = "#16213e"
CARD = "#0f3460"
ACCENT = "#e94560"
ACCENT2 = "#4fc3f7"
TEXT = "#e0e0e0"
TEXT_DIM = "#8899aa"
MONO = ("Consolas", 9)

FONT_H1 = ("Segoe UI", 17, "bold")
FONT_H2 = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 9)
FONT_BIG = ("Segoe UI", 22, "bold")


class IntervalTimerView:
    def __init__(
        self,
        root: tk.Tk,
        *,
        audio_backend: str | None,
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        on_browse_sound: Callable[[], None],
        on_reset_sound: Callable[[], None],
        on_close: Callable[[], None],
    ):
        self.root = root
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_browse_sound = on_browse_sound
        self._on_reset_sound = on_reset_sound
        self._on_close_cb = on_close

        self.root.title("Interval Timer")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.sound_path: str = ""
        self.sound_label = tk.StringVar(value="")

        self.countdown_var = tk.StringVar(value="—")
        self.next_time_var = tk.StringVar(value="—")
        self.remaining_var = tk.StringVar(value="—")
        self.status_var = tk.StringVar(value="Bereit")

        self._build_ui(audio_backend)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self, audio_backend: str | None) -> None:
        root = self.root

        hdr = tk.Frame(root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(hdr, text="⏱  Interval Timer", font=FONT_H1, bg=BG, fg=TEXT).pack(
            side="left"
        )
        backend_txt = f"Audio: {audio_backend or 'Fallback (kein Ton)'}"
        tk.Label(hdr, text=backend_txt, font=FONT_BODY, bg=BG, fg=TEXT_DIM).pack(
            side="right", anchor="s", pady=4
        )

        sep = tk.Frame(root, bg=ACCENT, height=2)
        sep.pack(fill="x", padx=20, pady=(0, 12))

        card = self._card(root, " Einstellungen ")
        card.pack(fill="x", padx=20, pady=4)

        self._row(
            card,
            "Startzeit (HH:MM):",
            (self._entry, {"name": "start_time", "width": 9, "default": datetime.datetime.now().strftime("%H:%M")}),
        )
        self._row(
            card,
            "Intervall (Minuten):",
            (self._entry, {"name": "interval", "width": 9, "default": "10"}),
        )
        self._row(
            card,
            "Anzahl Töne:",
            (self._entry, {"name": "count", "width": 9, "default": "5"}),
        )

        sf = tk.Frame(card, bg=SURFACE)
        tk.Label(
            sf,
            text="Tondatei:",
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT,
            width=18,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=4)

        inner = tk.Frame(sf, bg=SURFACE)
        inner.grid(row=0, column=1, sticky="w")

        tk.Label(
            inner,
            textvariable=self.sound_label,
            font=FONT_BODY,
            bg=CARD,
            fg=ACCENT2,
            width=22,
            anchor="w",
            padx=4,
            pady=2,
            relief="flat",
        ).pack(side="left", padx=(0, 6))

        self._btn(inner, "📂", self._on_browse_sound, small=True).pack(
            side="left", padx=2
        )
        self._btn(inner, "↩", self._on_reset_sound, small=True).pack(
            side="left", padx=2
        )
        sf.pack(fill="x", padx=10, pady=2)

        bf = tk.Frame(root, bg=BG)
        bf.pack(pady=10)
        self.start_btn = self._btn(bf, "▶  Starten", self._on_start, w=14)
        self.start_btn.pack(side="left", padx=8)
        self.stop_btn = self._btn(bf, "⏹  Stoppen", self._on_stop, w=14, accent=False)
        self.stop_btn.pack(side="left", padx=8)
        self.stop_btn.configure(state="disabled")

        sc = self._card(root, " Status ")
        sc.pack(fill="x", padx=20, pady=4)

        tk.Label(sc, textvariable=self.countdown_var, font=FONT_BIG, bg=SURFACE, fg=ACCENT2).pack(
            anchor="center", pady=(8, 2)
        )
        tk.Label(sc, text="bis zum nächsten Ton", font=FONT_BODY, bg=SURFACE, fg=TEXT_DIM).pack(
            anchor="center"
        )

        details = tk.Frame(sc, bg=SURFACE)
        details.pack(fill="x", padx=10, pady=8)

        self._status_row(details, 0, "Nächster Ton um:", self.next_time_var)
        self._status_row(details, 1, "Töne verbleibend:", self.remaining_var)
        self._status_row(details, 2, "Status:", self.status_var)

        lc = self._card(root, " Log ")
        lc.pack(fill="x", padx=20, pady=(4, 16))

        self.log_text = tk.Text(
            lc,
            height=6,
            width=54,
            bg=BG,
            fg=TEXT_DIM,
            font=MONO,
            state="disabled",
            relief="flat",
            insertbackground=TEXT,
            selectbackground=CARD,
        )
        sb = tk.Scrollbar(lc, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=4)
        sb.pack(side="right", fill="y", pady=4, padx=(0, 4))

    # ── UI-Helfer ───────────────────────────────────────────────────────────

    def _card(self, parent: tk.Misc, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg=ACCENT, bd=0)
        outer.pack_propagate(False)
        tk.Label(outer, text=title, font=FONT_H2, bg=ACCENT, fg=BG, padx=6).pack(
            anchor="w"
        )
        inner = tk.Frame(outer, bg=SURFACE, padx=8, pady=6)
        inner.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        return inner

    def _row(self, parent: tk.Misc, label: str, widget_spec) -> None:
        f = tk.Frame(parent, bg=SURFACE)
        tk.Label(
            f,
            text=label,
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT,
            width=18,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=4)

        constructor, kwargs = widget_spec
        constructor(f, **kwargs).grid(row=0, column=1, sticky="w", padx=4)
        f.pack(fill="x", padx=10, pady=2)

    def _entry(self, parent: tk.Misc, name: str, width: int, default: str) -> tk.Entry:
        var = tk.StringVar(value=default)
        setattr(self, f"{name}_var", var)
        return tk.Entry(
            parent,
            textvariable=var,
            width=width,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=FONT_BODY,
        )

    def _btn(
        self,
        parent: tk.Misc,
        text: str,
        cmd: Callable[[], None],
        w: int = 10,
        *,
        accent: bool = True,
        small: bool = False,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=ACCENT if accent else CARD,
            fg="#fff",
            activebackground=ACCENT2 if accent else ACCENT,
            activeforeground="#fff",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 8) if small else FONT_H2,
            width=w if not small else 3,
            padx=0 if small else 6,
            pady=3,
        )

    def _status_row(self, parent: tk.Misc, row: int, label: str, var: tk.StringVar) -> None:
        tk.Label(
            parent,
            text=label,
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT_DIM,
            anchor="w",
            width=20,
        ).grid(row=row, column=0, sticky="w", pady=2)
        tk.Label(
            parent,
            textvariable=var,
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT,
            anchor="w",
        ).grid(row=row, column=1, sticky="w", padx=8)

    # ── Public API (Controller → View) ──────────────────────────────────────

    def set_sound(self, path: str, label: str) -> None:
        self.sound_path = path
        self.sound_label.set(label)

    def ask_sound_file(self) -> str:
        return filedialog.askopenfilename(
            title="Tondatei auswählen",
            filetypes=[("Audio", "*.wav *.mp3 *.ogg"), ("Alle Dateien", "*.*")],
        )

    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str) -> None:
        messagebox.showinfo(title, message)

    def get_raw_inputs(self) -> tuple[str, str, str]:
        return (
            self.start_time_var.get().strip(),
            self.interval_var.get().strip(),
            self.count_var.get().strip(),
        )

    def set_running(self, running: bool) -> None:
        self.start_btn.configure(state="disabled" if running else "normal")
        self.stop_btn.configure(state="normal" if running else "disabled")

    def reset_status(self) -> None:
        self.status_var.set("Bereit")
        self.countdown_var.set("—")
        self.next_time_var.set("—")
        self.remaining_var.set("—")

    def update_countdown(self, text: str) -> None:
        self.countdown_var.set(text)

    def update_next_time(self, text: str) -> None:
        self.next_time_var.set(text)

    def update_remaining(self, text: str) -> None:
        self.remaining_var.set(text)

    def update_status(self, text: str) -> None:
        self.status_var.set(text)

    def call_in_ui_thread(self, fn: Callable, *args, **kwargs) -> None:
        self.root.after(0, fn, *args, **kwargs)

    def log(self, msg: str) -> None:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ── Window close ───────────────────────────────────────────────────────

    def _on_close(self) -> None:
        self._on_close_cb()
