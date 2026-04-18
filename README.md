# PyGong

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/PRIArobotics/PyGong/build-release.yml?branch=main)](https://github.com/PRIArobotics/PyGong/actions)
[![Latest Release](https://img.shields.io/github/v/release/PRIArobotics/PyGong)](https://github.com/PRIArobotics/PyGong/releases)

Ein einfacher **Interval Timer** mit GUI, der ab einer eingegebenen Startzeit in regelmäßigen Abständen einen Ton (Gong) abspielt – auch wenn die Startzeit bereits in der Vergangenheit liegt.

## Zweck

PyGong wurde entwickelt, um **Trainingszeiten für die [ECER](https://ecer.pria.at) (European Conference on Educational Robotics) zu takten und zu vereinfachen**. 

In Robotik-Wettbewerben ist präzises Zeitmanagement entscheidend:
- **Strukturiert Training**: Definiere feste Trainingsphasen mit automatischen Übergängen
- **Faire Bedingungen**: Alle Teams trainieren nach dem gleichen Zeitschema
- **Konsistenz**: Automatisiertes Timing eliminiert manuelle Fehler

## Features

- **GUI-basierter Timer** mit PyQt6
- **Ab der eingegebenen Zeit starten** – auch wenn diese bereits vorbei ist
- **Verschiedene Gongs wählbar** aus dem `gongs/` Ordner oder eigene Dateien
- **Sound während Laufzeit umschalten** – ohne Timer zu stoppen
- **Live-Log** mit allen Ereignissen
- **Konfigurierbar**: Startzeit, Intervall, Anzahl der Töne

## Installation

### Voraussetzungen
- Python 3.9 oder höher
- PyQt6

### Aus den Quellen

```bash
# Repository klonen
git clone https://github.com/PRIArobotics/PyGong.git
cd PyGong

# Virtuelle Umgebung erstellen (optional, aber empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate  # Windows

# Laufzeit-Abhängigkeiten installieren
pip install -r requirements.txt

# Optional: Dev/Build-Tools installieren (z.B. PyInstaller)
pip install -r requirements-dev.txt
```

### Ausführbare Datei (Releases)

Laden Sie die vorkompilierte Executable für Ihr Betriebssystem von den [Releases](https://github.com/PRIArobotics/PyGong/releases) herunter:
- **Windows**: `PyGong.exe`
- **macOS**: `PyGong`
- **Linux**: `PyGong`

## Verwendung

### Aus den Quellen starten

```bash
python interval_timer.py
```

### Executable ausführen

Einfach doppelklick auf die ausführbare Datei oder von der Kommandozeile aus ausführen.

### In der Anwendung

1. **Startzeit**: Geben Sie die Uhrzeit ein, zu der der erste Gong abgespielt werden soll (HH:MM)
2. **Intervall**: Definieren Sie das Intervall in Minuten zwischen den Gongs
3. **Anzahl Töne**: Bestimmen Sie, wie viele Gongs abgespielt werden sollen
4. **Sounddatei**: Wählen Sie einen vorkonfigurierten Gong aus oder laden Sie eine eigene Datei
5. **Starten**: Klicken Sie auf "Starten" und beobachten Sie das Live-Log

**Hinweis**: Sie können den Gong jederzeit während des Laufs umschalten – der nächste Gong wird mit dem neuen Sound abgespielt.

## Erstelle deine eigenen Gongs

Legen Sie WAV-, MP3-, OGG- oder FLAC-Dateien in den `gongs/` Ordner:

```
PyGong/
├── interval_timer.py
├── gongs/
│   ├── bell.wav
│   ├── gong.mp3
│   └── chime.ogg
└── ...
```

Die Dateien werden automatisch im Sound-Dropdown aufgelistet.

## Entwicklung

Weitere Informationen für Entwickler finden Sie in [CONTRIBUTING.md](CONTRIBUTING.md).

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

## Support

Fragen, Bugs oder Feature-Requests? Erstellen Sie ein [Issue](https://github.com/PRIArobotics/PyGong/issues) oder einen [Pull Request](https://github.com/PRIArobotics/PyGong/pulls).
