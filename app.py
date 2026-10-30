"""Flask entry point for the local SWOT and PESTLE assistant."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from flask import Flask, jsonify, render_template, request

from analysis import CATEGORIES, generate_analysis


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "ANALYSIS_DATABASE", str(Path(app.instance_path) / "analyses.sqlite3")
        ),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect_db() -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_db() -> None:
        with connect_db() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    description TEXT NOT NULL,
                    analysis_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    initialize_db()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/analyze")
    def analyze():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Send the form as a JSON object."}), 400
        name, industry, description, error = validate_inputs(payload)
        if error:
            return jsonify({"error": error}), 400
        return jsonify(
            {
                "name": name,
                "industry": industry,
                "description": description,
                "analysis": generate_analysis(name, industry, description),
            }
        )

    @app.get("/api/analyses")
    def list_analyses():
        with connect_db() as db:
            rows = db.execute(
                "SELECT id, name, industry, created_at FROM analyses "
                "ORDER BY id DESC LIMIT 100"
            ).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.post("/api/analyses")
    def save_analysis():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Send the analysis as a JSON object."}), 400
        name, industry, description, error = validate_inputs(payload)
        if error:
            return jsonify({"error": error}), 400
        analysis = payload.get("analysis")
        if not isinstance(analysis, dict) or set(analysis) != set(CATEGORIES):
            return jsonify({"error": "Include all ten analysis categories."}), 400
        cleaned: dict[str, list[str]] = {}
        for category in CATEGORIES:
            items = analysis[category]
            if (
                not isinstance(items, list)
                or not items
                or len(items) > 10
                or any(not isinstance(item, str) or not item.strip() for item in items)
            ):
                return jsonify(
                    {"error": f"{category} must contain 1 to 10 non-empty points."}
                ), 400
            cleaned[category] = [item.strip()[:500] for item in items]

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with connect_db() as db:
            cursor = db.execute(
                "INSERT INTO analyses (name, industry, description, analysis_json, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, industry, description, json.dumps(cleaned), created_at),
            )
            analysis_id = cursor.lastrowid
        return jsonify(
            {
                "id": analysis_id,
                "name": name,
                "industry": industry,
                "created_at": created_at,
            }
        ), 201

    @app.get("/api/analyses/<int:analysis_id>")
    def get_analysis(analysis_id: int):
        with connect_db() as db:
            row = db.execute(
                "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        if row is None:
            return jsonify({"error": "Saved analysis not found."}), 404
        return jsonify(
            {
                "id": row["id"],
                "name": row["name"],
                "industry": row["industry"],
                "description": row["description"],
                "analysis": json.loads(row["analysis_json"]),
                "created_at": row["created_at"],
            }
        )

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"error": "Request is too large. Shorten the description."}), 413

    return app


def validate_inputs(payload: dict[str, Any]) -> tuple[str, str, str, str | None]:
    fields = {
        "name": ("Business or project name", 100),
        "industry": ("Industry", 100),
        "description": ("Description", 3000),
    }
    values: dict[str, str] = {}
    for key, (label, maximum) in fields.items():
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            return "", "", "", f"{label} is required."
        value = value.strip()
        if len(value) > maximum:
            return "", "", "", f"{label} must be {maximum} characters or fewer."
        values[key] = value
    return values["name"], values["industry"], values["description"], None


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
