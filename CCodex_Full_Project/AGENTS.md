# AGENTS instructions (Repo Root)

## Ziel
Read-only Live-Farm-Analytics auf Basis von Screen-Capture + OCR/Template Matching.

## Guardrails (verbindlich)
- Nur Pixelanalyse aus Fensterframes (read-only).
- Kein Memory Reading, kein Hooking, keine Prozessinjektion.
- Keine Maus-/Tastatur-Simulation, keine Spielautomatisierung.
- Kein Anti-Cheat-Bypass.
- Features immer optional per Config toggelbar implementieren.
- Stabilität (ROI/OCR/Parsing) priorisieren, dann optionale ML-Ansätze.

## Setup
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Entwickeln / Ausführen
```bash
python main.py --debug --layout config/layout.json
python main.py --debug-ocr --db on --db-path output/farm.db
```

## Test/Lint/Checks
```bash
python -m compileall .
python tests/test_event_builder.py
python tests/test_debounce.py
```

## Hinweise
- ROIs in `config/layout.json` immer relativ (`0..1`) speichern.
- Änderungen an Parsing-Regeln in README kurz dokumentieren.
