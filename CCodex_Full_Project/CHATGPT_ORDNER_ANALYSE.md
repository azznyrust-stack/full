# Detaillierte ChatGPT-Ordneranalyse

Diese Datei dokumentiert **alle Dateien** im Projektordner und beschreibt, welche Aufgabe sie haben. Für Python-Dateien sind zusätzlich die enthaltenen Funktionen/Klassen mit Zweck erklärt.

## 1) Projektüberblick

Das Projekt ist eine **Read-only Live-Farm-Analytics-Pipeline**: Es liest Bildausschnitte eines Spielfensters, extrahiert Zahlen/Text per OCR, erzeugt Events (z. B. Loot/Kill/Dungeon), berechnet Statistiken und kann Daten in SQLite speichern.

---

## 2) Vollständiges Datei-Inventar (aktuell)

Diese Liste enthält **jede Datei**, die aktuell im Ordner vorhanden ist:

- `AGENTS.md`
- `CHATGPT_ORDNER_ANALYSE.md`
- `README.md`
- `main.py`
- `requirements.txt`
- `capture/__init__.py`
- `capture/capture_backend.py`
- `capture/window_finder.py`
- `config/__init__.py`
- `config/layout.json`
- `core/__init__.py`
- `core/debounce.py`
- `core/event_builder.py`
- `core/pipeline.py`
- `core/stats.py`
- `core/telemetry.py`
- `output/__init__.py`
- `output/storage_sqlite.py`
- `tests/test_debounce.py`
- `tests/test_event_builder.py`
- `tools/__init__.py`
- `tools/calibrate_ocr.py`
- `tools/roi_tuner.py`
- `vision/__init__.py`
- `vision/motion.py`
- `vision/ocr.py`
- `vision/ocr_text.py`

---

## 3) Datei-für-Datei Dokumentation

## Root-Dateien

### `AGENTS.md`
- Enthält verbindliche Arbeitsrichtlinien für den Agenten im Repository.
- Schwerpunkt: Read-only Pixelanalyse, keine Automatisierung/Injection/Bypass.

### `README.md`
- Projektbeschreibung, Guardrails, Setup, Startbefehle, Troubleshooting.
- Dokumentiert Laufzeitoptionen (`--debug`, `--debug-ocr`, `--db`, ...).

### `CHATGPT_ORDNER_ANALYSE.md`
- Diese Analyse-Datei mit vollständigem Datei-Inventar und Funktionsübersicht.
- Dient als schnelle Onboarding- und Nachschlage-Dokumentation.

### `main.py`
- Minimaler Einstiegspunkt.
- Importiert und startet die Hauptpipeline.
- **Ablauf:** `run()` aus `core/pipeline.py` wird aufgerufen.

### `requirements.txt`
- Python-Abhängigkeiten:
  - `numpy` (Array/Mathe)
  - `opencv-python` (Bildverarbeitung/GUI)
  - `mss` (Screen-Capture)
  - `pywin32` (Fenstersuche unter Windows)
  - `pytesseract` (OCR)

---

## `capture/`

### `capture/__init__.py`
- Package-Marker, keine Logik.

### `capture/capture_backend.py`
- Verantwortlich für das Erfassen von Bildschirmregionen.
- **Klasse `MSSCapture`**
  - `__init__`: Initialisiert `mss`-Capture-Kontext.
  - `grab_region(x, y, w, h)`: Nimmt einen Frame-Ausschnitt auf und gibt ein BGR-Bild (NumPy) zurück.

### `capture/window_finder.py`
- Fensterlokalisierung und Koordinatenumrechnung.
- **Funktionen:**
  - `find_window_by_title_substring(substr)`: Sucht sichtbare Windows-Fenster, deren Titel den Suchstring enthält.
  - `get_client_rect_screen(hwnd)`: Liefert Clientbereich eines Fensters in Bildschirmkoordinaten (`x, y, w, h`).

---

## `config/`

### `config/__init__.py`
- Package-Marker, keine Logik.

### `config/layout.json`
- Zentrale Konfiguration:
  - `window_title_contains`: Suchstring für das Spielfenster.
  - `rois`: Relative ROI-Definitionen (`x,y,w,h` in 0..1) für Gold/Chat/Dungeon/Kill.
  - `parsing`: Regex + Keywords für Loot/Kill/Dungeon-Start/-Ende.
  - `smoothing`: OCR-/Event-Glättung (`median_window`, `stable_frames`, `event_cooldown_ms`, `max_gold_jump`).
  - `session`: DB-Pfad + Autosave-Intervall.

---

## `core/`

### `core/__init__.py`
- Package-Marker, keine Logik.

### `core/debounce.py`
- Entprellung/Filter gegen OCR-Flattern und Event-Duplikate.
- **Klasse `EventDebouncer`**
  - `__init__(cooldown_ms, stable_frames)`: Konfiguriert Cooldown und notwendige stabile Frames.
  - `make_hash(payload)`: Erzeugt stabilen SHA1-Hash für Event-Payloads.
  - `allow(key, payload_hash, now_ms=None)`: Entscheidet, ob ein Event emittiert werden darf (stabil genug + Cooldown erfüllt).

### `core/event_builder.py`
- Übersetzt Telemetriedaten in semantische Events.
- **Klasse `EventBuilder`**
  - `__init__(layout)`: Lädt Parsing-Regex/Keywords + Debounce-Einstellungen.
  - `_contains_any(text, keywords)`: Keyword-Helper.
  - `build(telemetry, now_ts=None)`: Erstellt Eventliste aus Telemetrie:
    - Goldänderung → `GOLD_GAIN` / `GOLD_SPEND`
    - Chat-Matches → `LOOT`, `KILL`
    - Dungeon-Text → `DUNGEON_START`, `DUNGEON_END`, `DUNGEON_STATE`
    - Killcounter-Anstieg → `KILL`

### `core/telemetry.py`
- Extrahiert rohe Telemetrie aus dem Frame via ROI + OCR.
- **Funktion `crop(frame, roi)`**: Schneidet ROI aus dem Frame, inklusive 0..1-Clamping.
- **Klasse `TelemetryExtractor`**
  - `__init__(layout)`: Lädt ROIs und initialisiert Digit-Glättung.
  - `extract(frame)`: Liefert strukturierte Telemetrie:
    - `gold`
    - `chat_text`
    - `dungeon_text`
    - `dungeon_counter`
    - `kill_counter`
    - `debug` (OCR-Zwischenbilder/Text)

### `core/stats.py`
- Aggregiert Events zu Session-Statistiken.
- **Klasse `FarmStats`**
  - `__init__(prices_path=None, csv_path=None)`: Initialisiert Zähler/Timer, lädt optionale Preislisten, optional CSV-Export.
  - `_load_prices(prices_path)`: Lädt JSON-Preiszuordnung für Loot-Bewertung.
  - `_init_csv()`: Erstellt CSV mit Headern.
  - `_append_csv(snapshot)`: Hängt Snapshot-Zeile in CSV an.
  - `update_telemetry(telemetry)`: Aktualisiert Gold-Start/Gold-Now.
  - `apply_events(events)`: Erhöht Counters (Gains, Spends, Kills, Dungeons, Loot-Liste).
  - `snapshot()`: Berechnet aktuellen Snapshot inkl. Raten pro Stunde und optionalem Lootwert.

### `core/pipeline.py`
- Orchestriert den Gesamtablauf zur Laufzeit.
- **Funktionen:**
  - `draw_rois(frame, rois)`: Zeichnet ROI-Overlays auf Debug-Frame.
  - `parse_args()`: CLI-Argumente (`layout`, `fps`, `debug`, `debug-ocr`, `db`, `db-path`, `snapshot-interval`).
  - `run()`: Hauptloop:
    1. Layout laden + Fenster suchen
    2. Frame capturen
    3. Telemetrie extrahieren
    4. Events bauen
    5. Statistiken aktualisieren
    6. Optional in SQLite schreiben
    7. Optional Debugfenster rendern

---

## `vision/`

### `vision/__init__.py`
- Package-Marker, keine Logik.

### `vision/motion.py`
- Einfache Bewegungsmetrik zwischen Frames.
- **Klasse `MotionDetector`**
  - `__init__`: Initialisiert Vorframe.
  - `score(frame)`: Graustufen-Differenz zum Vorframe als normalisierten Bewegungswert (`0..1`).

### `vision/ocr.py`
- OCR für numerische Felder (z. B. Gold/Killcounter).
- **Klasse `DigitSmoother`**
  - `__init__(window=5, max_jump=5_000_000)`: Medianfenster + Ausreißerlimit.
  - `update(value)`: Stabilisiert Messwerte (Median + Jump-Filter).
- **Funktionen:**
  - `_preprocess_digits(bgr)`: Vergrößerung + Otsu-Threshold für OCR-Vorbereitung.
  - `ocr_digits(bgr, return_debug=False)`: Liest Zahl mit Tesseract (`Whitelist 0-9`) und gibt optional Debugdaten zurück.

### `vision/ocr_text.py`
- OCR für mehrzeilige Text-ROIs (Chat/Dungeonstatus).
- **Funktionen:**
  - `preprocess_text_roi(bgr)`: Graustufe + Upscaling + Blur + adaptive Threshold.
  - `ocr_text_multiline(bgr)`: OCR mit `--psm 6`, bereinigt Leerzeilen und liefert Text + Debugdaten.

---

## `output/`

### `output/__init__.py`
- Package-Marker, keine Logik.

### `output/storage_sqlite.py`
- Persistenzschicht für Sessiondaten.
- **Klasse `SQLiteStorage`**
  - `__init__(db_path, flush_interval_s=3)`: DB öffnen, Verzeichnis anlegen, Schema sicherstellen.
  - `_create_schema()`: Tabellen `events`, `snapshots`, `session` erzeugen.
  - `write_session_meta(meta)`: Session-Metadaten speichern.
  - `write_events(events)`: Eventliste speichern.
  - `write_snapshot(snapshot)`: Snapshot speichern.
  - `_maybe_flush()`: Commit nach Intervall.
  - `close()`: Finaler Commit + Connection schließen.

---

## `tools/`

### `tools/__init__.py`
- Package-Marker, keine Logik.

### `tools/calibrate_ocr.py`
- Live-Hilfstool zum OCR-Tuning pro ROI.
- **Funktionen:**
  - `parse_args()`: Argumente `--layout`, `--roi`, `--mode` (`digits|text`).
  - `main()`: Captured ROI live und zeigt Preprocessing-Stufen (`gray`, `scaled`, `threshold`) zur Feinjustierung.

### `tools/roi_tuner.py`
- Live-Hilfstool zum Anzeigen/Verwalten von ROI-Definitionen.
- **Funktionen:**
  - `parse_args()`: Argument `--layout`.
  - `main()`: Zeichnet ROIs über Liveframe; erlaubt Navigieren/Löschen/Speichern (`n/p/d/s`).

---

## `tests/`

### `tests/test_debounce.py`
- Einfacher Laufzeittest für EventDebouncer.
- **Funktion `main()`**:
  - Prüft Stable-Frame-Logik + Cooldown-Verhalten per Assertions.

### `tests/test_event_builder.py`
- Einfacher Laufzeittest für EventBuilder.
- **Konstanten + Funktion:**
  - `LAYOUT`: Testlayout mit Parsing/Smoothing.
  - `main()`: Erzeugt Testtelemetrie und prüft erwartete Events (`LOOT`, `KILL`, `DUNGEON_START`, `GOLD_GAIN`, `DUNGEON_END`).

---

## 4) Kurzfazit zur Ordnerstruktur

- **capture/**: Frame- und Fensterzugriff
- **vision/**: OCR/Preprocessing/Bewegung
- **core/**: Logik (Telemetrie → Events → Stats → Laufpipeline)
- **output/**: Speicherung in SQLite
- **tools/**: Kalibrier- und Tuningtools
- **tests/**: Schnelltests
- **config/**: Laufzeitkonfiguration

