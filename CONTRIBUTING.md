# Contributing to PyGong

Vielen Dank für dein Interesse an der Mitarbeit an PyGong! Dieses Dokument gibt dir einen Überblick über den Beitragsprozess.

## Code of Conduct

Alle Beiträge sollten respektvoll und konstruktiv sein. Wir verbieten Belästigung, Diskriminierung oder andere Verhaltensweisen, die die Gemeinschaft schaden.

## Wie man beiträgt

### Bugs berichten

Fehler können durch das Erstellen eines [Issue](https://github.com/PRIArobotics/PyGong/issues) gemeldet werden. Bitte include:

- **Beschreibung**: Klar und prägnant erklären, was nicht funktioniert
- **Reproduktionsschritte**: Schritt-für-Schritt Anleitung zum Reproduzieren des Fehlers
- **Erwartetes Verhalten**: Was sollte passieren?
- **Tatsächliches Verhalten**: Was passiert stattdessen?
- **Umgebung**: Betriebssystem, Python-Version, PyQt6-Version, etc.
- **Logs/Screenshots**: Helfen bei der Diagnose

### Feature-Anfragen

Haben Sie eine Idee für eine neue Funktion? Bitte erstellen Sie ein [Issue](https://github.com/PRIArobotics/PyGong/issues) mit:

- **Beschreibung**: Erklären Sie die Idee klar
- **Motiviation**: Warum ist das Feature nützlich?
- **Alternativen**: Gibt es andere Wege, dies zu lösen?
- **Zusätzlicher Kontext**: Links oder Referenzen, die hilfreich sind

### Pull Requests einreichen

1. **Fork das Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PyGong.git
   cd PyGong
   ```

2. **Erstelle einen Feature-Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Lokale Umgebung einrichten**
   ```bash
   python -m venv venv
   source venv/bin/activate  # oder venv\Scripts\activate auf Windows
   pip install -r requirements.txt
   ```

4. **Mache deine Änderungen**
   - Schreibe sauberen, wohlskriptierten Code
   - Folge den bestehenden Konventionen im Projekt
   - Aktualisiere die Dokumentation, wenn nötig

5. **Teste deine Änderungen**
   ```bash
   python interval_timer.py
   ```

6. **Committen und Pushen**
   ```bash
   git add .
   git commit -m "Add: Amazing feature (#123)"
   git push origin feature/AmazingFeature
   ```

7. **Erstelle einen Pull Request**
   - Gehe zu deinem Fork auf GitHub
   - Klicke auf "Compare & pull request"
   - Gib eine klare Beschreibung der Änderungen an
   - Verknüpfe zugehörige Issues mit `Closes #123`
   - Warte auf Review

## Code-Stil

Das Projekt verwendet **PEP 8** als Richtlinie:

- **Indentation**: 4 Spaces
- **Zeilenlänge**: max. 100 Zeichen
- **Imports**: Sortiert und gruppiert
- **Docstrings**: Google-Style Docstrings für öffentliche Funktionen
- **Type Hints**: Wo sinnvoll, verwende Type Hints

### Beispiel

```python
def compute_skipped_intervals(
    *,
    now: datetime.datetime,
    start_dt: datetime.datetime,
    interval_sec: float,
) -> int:
    """Wie viele Intervalle seit start_dt bereits vergangen sind (>= 0).
    
    Args:
        now: Aktuelle Zeit
        start_dt: Startzeit des Timers
        interval_sec: Intervalllänge in Sekunden
        
    Returns:
        Anzahl der bereits vergangenen Intervalle
    """
```

## Projektstruktur

```
PyGong/
├── interval_timer.py          # Einstiegspunkt
├── pygong/
│   ├── __init__.py
│   ├── model.py               # Datenmodelle & Timer-Logik
│   ├── view.py                # PyQt6 GUI-Komponenten
│   └── controller.py          # Event-Handler & Geschäftslogik
├── gongs/                     # Standard-Gongs (wird beim Build ignoriert)
├── .github/
│   └── workflows/
│       └── build-release.yml  # CI/CD Pipeline
├── requirements.txt           # Python-Abhängigkeiten
├── README.md
├── CONTRIBUTING.md           # Dieses Dokument
└── LICENSE
```

### MVC-Architektur

- **Model** (`model.py`): Timer-Logik, Sound-Generierung, Interval-Berechnung
- **View** (`view.py`): PyQt6 GUI, Input-Verarbeitung
- **Controller** (`controller.py`): Verbindung zwischen Model und View, Event-Handling

## Versionierung

Dieses Projekt folgt [Semantic Versioning](https://semver.org/):

- **Major**: Brechende Änderungen (z.B. GUI-Umstrukturierung)
- **Minor**: Neue Features, abwärtskompatibel
- **Patch**: Bug-Fixes

## Release-Prozess

1. Updates in `README.md` und `CONTRIBUTING.md` vornehmen (falls nötig)
2. Commits mit Feature/Bug-Fixes
3. Git-Tag mit Version erstellen:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
4. GitHub Actions buildet automatisch Executables und erstellt ein Release

## Hilfreiche Links

- [PyQt6 Dokumentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

## Fragen?

- Erstelle ein [Issue](https://github.com/PRIArobotics/PyGong/issues) mit tag `question`
- Oder diskutiere in [Discussions](https://github.com/PRIArobotics/PyGong/discussions)

Danke, dass du PyGong besser machst! 🎵
