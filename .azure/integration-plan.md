# Local integration notes

- Backend: project root; `python app.py`; Flask default port `5000`; build: not applicable; health: `GET /api/health`.
- Frontend: Flask-served `templates/index.html`; assets `static/app.js`, `static/app.css`; run/build: no separate frontend build. External analysis/API dependencies: none.
- API seam: `static/app.js` `api()` helper, same-origin `/api/*` endpoints.
- Mock files to remove: none; suggestions are generated locally in `analysis.py`. Locally duplicated types and preview-state switcher: none.
- API routes: `GET /api/health`; `POST /api/analyze`; `GET /api/analyses`; `POST /api/analyses`; `GET /api/analyses/<id>`.
- Database: SQLite at `instance/analyses.sqlite3` (override with `ANALYSIS_DATABASE`); built-in `sqlite3` schema initialization; migration tool/directory: none; connection configuration: `ANALYSIS_DATABASE`; no migrations or seed data.
- Shared types: none; JSON contracts are validated by Flask.
- Services: Flask app and SQLite; Essential. Enhancement services: none. No external AI/API services.
