"""Pruebas de inicialización, aislamiento y restricciones de SQLite."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import db
from app import main
from app.main import create_app


def test_initialization_creates_schema_and_enables_foreign_keys(database_path):
    db.init_db(database_path)
    db.init_db(database_path)

    with db.get_connection(database_path) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        foreign_keys_enabled = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]
        foreign_keys = connection.execute(
            "PRAGMA foreign_key_list(tareas)"
        ).fetchall()

    assert {"materias", "tareas"} <= tables
    assert foreign_keys_enabled == 1
    assert len(foreign_keys) == 1
    assert foreign_keys[0]["table"] == "materias"
    assert foreign_keys[0]["on_delete"] == "RESTRICT"


def test_database_path_uses_environment_setting(monkeypatch, tmp_path):
    configured_path = tmp_path / "datos" / "prueba.sqlite3"
    monkeypatch.setenv("UPB_TASKS_DB_PATH", str(configured_path))

    assert db.get_database_path() == configured_path


def test_empty_database_path_is_rejected():
    with pytest.raises(ValueError, match="no puede estar vacío"):
        db.get_database_path("")


def test_schema_rejects_invalid_data_and_restricts_deleting_subject(database_path):
    db.init_db(database_path)

    with db.get_connection(database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO materias (nombre, color) VALUES (?, ?)",
                ("", "#3366CC"),
            )

        subject = connection.execute(
            "INSERT INTO materias (nombre, color) VALUES (?, ?)",
            ("Matemáticas", "#3366CC"),
        )
        subject_id = subject.lastrowid
        connection.execute(
            """
            INSERT INTO tareas (
                materia_id, titulo, descripcion, vencimiento_utc,
                zona_horaria, tipo_vencimiento, fecha_local
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subject_id,
                "Taller",
                None,
                "2026-10-27T00:00:00+00:00",
                "America/Bogota",
                "fecha",
                "2026-10-26",
            ),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("DELETE FROM materias WHERE id = ?", (subject_id,))


def test_app_factory_initializes_injected_database(client, app, database_path):
    assert app.state.db_path == database_path
    assert database_path.exists()
    assert isinstance(client, TestClient)


def test_app_serves_root_and_static_files(monkeypatch, tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<h1>Inicio</h1>", encoding="utf-8")
    (static_dir / "styles.css").write_text("body {}", encoding="utf-8")
    monkeypatch.setattr(main, "STATIC_DIR", static_dir)

    application = create_app(tmp_path / "organizador.sqlite3")
    with TestClient(application) as client:
        assert client.get("/").text == "<h1>Inicio</h1>"
        assert client.get("/static/styles.css").text == "body {}"
