# VisGuide — Module 1: Structured Data Visualization

## Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```
Settings default to `config.settings.local` (see `manage.py`). Copy
`.env.example` to `.env` and adjust as needed (not auto-loaded — wire in
`django-environ` or `python-dotenv` in `config/settings/local.py` if you
want `.env` picked up automatically).

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/datasets/upload/` | Upload a CSV/XLSX file (`file` form field) |
| GET | `/api/datasets/` | List datasets |
| GET | `/api/datasets/{id}/` | Dataset detail |
| GET | `/api/datasets/{id}/columns/` | Parsed columns |
| GET | `/api/datasets/{id}/profile/` | Analysis profile (types, quality, stats, correlation) |
| GET | `/api/datasets/{id}/recommendation/` | Recommended visualization type |
| POST | `/api/datasets/{id}/recommendation/refresh/` | Force a fresh recommendation |
| GET/POST | `/api/datasets/{id}/visualization-config/` | Standardized frontend-ready config |
| DELETE | `/api/datasets/{id}/` | Delete a dataset |

## End-to-end smoke test
```bash
python tests/integration/run_e2e_smoke.py
```
Runs five sample datasets (`tests/integration/sample_data/`) through the
full upload → parse → analyze → recommend → configure pipeline and prints
the result of each stage.

## Architecture
See the accompanying `visguide_architecture.md` for the full design
rationale, extension points, and how future modules (documents, 3D
scenes, AI recommendation) plug in without modifying this code.
