# Records Analytics API

Manage records and produce category counts, status counts, and total amounts for dashboards.

Portfolio learning project built with Python, FastAPI, Pydantic, and SQLite. Includes CRUD, status filtering, pagination, analytics, automated tests, and Docker packaging.

## Quick start (Python 3.10+)

```text
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# In another activated terminal:
python -m pytest -q
```

Open http://127.0.0.1:8000/docs. Use POST /records with sample.json, then GET /records/summary. The SQLite database is created automatically on startup.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Health check |
| POST | /records | Create |
| GET | /records | List; status, limit, offset filters |
| GET | /records/summary | Aggregate metrics |
| GET | /records/{item_id} | Read one |
| PUT | /records/{item_id} | Replace all fields |
| DELETE | /records/{item_id} | Delete |

## Docker

```sh
docker build -t records-analytics-api .
docker run --rm -p 8000:8000 -v records-analytics-api-data:/app/data records-analytics-api
```

## Structure

app/main.py: schemas, database access, lifecycle, API routes.
tests/test_api.py: isolated temporary database tests.
sample.json: example request. docs/: PDF walkthrough.

## Design and limitations

Synchronous endpoints keep blocking SQLite work out of the async event loop. SQL parameters separate input from query syntax. Connections use context managers for transactions. PUT replaces the complete record. Status summaries describe current stages, not historical conversion rates. No login or per-user isolation: run locally with sample data. Add authentication and authorization before shared deployment. JSON storage simplifies this beginner project; a larger system should use typed relational columns, migrations, indexes and PostgreSQL. Monetary amounts are illustrative floats, not accounting-grade decimal storage.

## GitHub upload

Create an empty repository named records-analytics-api. Extract this ZIP and upload the contents of the records-analytics-api folder, including app, tests, docs and README.md. Do not upload the ZIP itself as your source code. For hidden files and complete uploads, Git is preferred:

```sh
git init
git add .
git commit -m "Add FastAPI portfolio project"
git branch -M main
git remote add origin https://github.com/praveenkumarmandula/records-analytics-api.git
git push -u origin main
```

## Extend it yourself

Add authentication, a frontend with charts, date-based trends, PostgreSQL migrations and continuous integration. Understand and customize this project before describing it in an interview. Do not claim it as employer production work.

## References

https://fastapi.tiangolo.com/tutorial/body/
https://fastapi.tiangolo.com/tutorial/testing/
https://docs.python.org/3/library/sqlite3.html
