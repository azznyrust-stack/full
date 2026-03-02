# CCodex Full Project – Live Farm Analytics (Read-only)

Dieses Projekt analysiert ausschließlich Bilddaten aus einem Spiel-Fenster (Frame-Capture + OCR/Template-Matching), um Session-Analytics wie Profit, Monster-Kills, Dungeon-Runs und Reports zu berechnen.

## Guardrails / Compliance
- **Read-only Analyse:** Es werden nur Pixel des Fensters gelesen.
- **Keine Automatisierung:** Keine Maus-/Tastatursimulation, keine Zielauswahl-Logik, kein Bot-Verhalten.
- **Keine Prozess-Introspektion:** Kein Memory-Reading, kein Hooking, kein Anti-Cheat-Bypass.
- **Feature-Toggles:** Alle Analytics-Features sind über `config/layout.json` optional.

## Voraussetzungen
- Python 3.10+
- EasyOCR (wird über `requirements.txt` installiert)
- Windows (für `pywin32` Window-Discovery)

## Quickstart
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py --debug --layout config/layout.json
```

## OCR-Engine (EasyOCR)
Das Projekt verwendet **ausschließlich EasyOCR** (kein Tesseract).

Für flüssige Laufzeit wird intern eine einzelne Reader-Instanz wiederverwendet, damit pro Frame kein neues OCR-Modell geladen werden muss.

## Troubleshooting
- **Fenster nicht gefunden:** `window_title_contains` in `config/layout.json` an den exakten Fenstertitel anpassen.
- **Black screen capture:**
  - Spiel im **Windowed/Borderless** Modus starten.
  - Hardware-Overlay/Exklusiv-Vollbild deaktivieren.
  - Capture-Rechte prüfen (gleiches Privileg-Level wie das Spiel).
- **OCR instabil/langsam:**
  - ROI präziser setzen (`tools/roi_tuner.py`).
  - `smoothing`-Parameter in `config/layout.json` anpassen.
  - `--fps` schrittweise erhöhen und mit `--debug-ocr` validieren.

## Laufzeit-Optionen
```bash
python main.py \
  --layout config/layout.json \
  --fps 5 \
  --debug \
  --debug-ocr \
  --db on \
  --db-path output/farm.db \
  --snapshot-interval 1.0
```

## Smoke/Test Kommandos
```bash
python -m compileall .
python tests/test_event_builder.py
python tests/test_debounce.py
python tests/test_telemetry_crop.py
```

## Regex-/Parsing-Defaults
Die Standard-Regexes für Loot/Kill/Dungeon liegen in `config/layout.json` unter `parsing` und sind auf **deutsche Spielsprache** ausgelegt. Sie sind bewusst konservativ gewählt, um False-Positives zu reduzieren. Bei abweichender Spielsprache bitte Keywords/Patterns anpassen.
