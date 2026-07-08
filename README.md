# Thai Conflict-of-Laws Checker

A demo web app for simplified contract law selection under Thailand's Act on Conflict of Laws.

This tool helps determine which country's law is likely to apply when a contract dispute is filed with a Thai court.

Key behavior:

- If the contract expressly specifies a governing law, that law is selected.
- If both parties share the same nationality, that common nationality is selected.
- If the parties have different nationalities, the law of the place where the contract was made is selected.
- If Party 2's nationality must be resolved, the app supports both natural persons and juristic persons.

This is an educational demo only — not legal advice.

Files:

- `logic.py`: Core Python conflict-of-laws logic.
- `app.py`: Flask web app that guides the user through the decision flow.
- `templates/index.html`: User interface for the wizard.
- `tests/test_logic.py`: Pytest unit tests for core logic.
- `tests/test_app.py`: Integration tests for the wizard flow.

Run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Run tests:

```bash
pip install pytest
pytest -q
```
