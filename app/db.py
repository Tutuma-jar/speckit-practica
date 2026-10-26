"""Conexiones y esquema SQLite del organizador académico."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import sys
from collections.abc import Iterator


def get_database_path(configured_path: str | Path | None = None) -> Path:
    """Obtiene la ruta configurada o la carpeta de datos local del usuario."""
    if configured_path is not None:
        raw_path = str(configured_path)
    else:
        raw_path = os.environ.get("UPB_TASKS_DB_PATH")

    if raw_path is not None:
        if not raw_path.strip():
            raise ValueError("UPB_TASKS_DB_PATH no puede estar vacío.")
        return Path(raw_path).expanduser()

    if sys.platform == "win32":
        data_root = os.environ.get("LOCALAPPDATA")
        base_path = Path(data_root) if data_root else Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base_path = Path.home() / "Library" / "Application Support"
    else:
        data_root = os.environ.get("XDG_DATA_HOME")
        base_path = Path(data_root).expanduser() if data_root else Path.home() / ".local" / "share"

    return base_path / "UPB" / "OrganizadorTareas" / "organizador.sqlite3"


@contextmanager
def get_connection(db_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    """Abre una conexión breve con las claves foráneas activadas."""
    database_path = get_database_path(db_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_db(db_path: str | Path | None = None) -> None:
    """Crea las tablas iniciales si todavía no existen."""
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS materias (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL
                    CHECK (length(trim(nombre)) BETWEEN 1 AND 100),
                color TEXT NOT NULL
                    CHECK (
                        length(color) = 7
                        AND color GLOB '#[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'
                    )
            );

            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY,
                materia_id INTEGER NOT NULL,
                titulo TEXT NOT NULL
                    CHECK (length(trim(titulo)) BETWEEN 1 AND 150),
                descripcion TEXT
                    CHECK (
                        descripcion IS NULL
                        OR length(trim(descripcion)) <= 2000
                    ),
                vencimiento_utc TEXT NOT NULL,
                zona_horaria TEXT NOT NULL,
                tipo_vencimiento TEXT NOT NULL
                    CHECK (tipo_vencimiento IN ('fecha', 'fecha_hora')),
                fecha_local TEXT,
                estado TEXT NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente', 'completada')),
                FOREIGN KEY (materia_id)
                    REFERENCES materias (id)
                    ON DELETE RESTRICT,
                CHECK (
                    (tipo_vencimiento = 'fecha' AND fecha_local IS NOT NULL)
                    OR
                    (tipo_vencimiento = 'fecha_hora' AND fecha_local IS NULL)
                )
            );
            """
        )


def create_subject(
    db_path: str | Path,
    nombre: str,
    color: str,
) -> dict[str, int | str]:
    """Guarda una materia y devuelve sus datos persistidos."""
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO materias (nombre, color) VALUES (?, ?)",
            (nombre, color),
        )
        return {"id": int(cursor.lastrowid), "nombre": nombre, "color": color}


def list_subjects(db_path: str | Path) -> list[dict[str, int | str]]:
    """Lista materias en un orden estable."""
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, nombre, color FROM materias ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]


def subject_exists(db_path: str | Path, subject_id: int) -> bool:
    """Comprueba si existe la materia referenciada por una tarea."""
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT 1 FROM materias WHERE id = ?",
            (subject_id,),
        ).fetchone()
        return row is not None


def create_task(
    db_path: str | Path,
    *,
    materia_id: int,
    titulo: str,
    descripcion: str | None,
    vencimiento_utc: str,
    zona_horaria: str,
    tipo_vencimiento: str,
    fecha_local: str | None,
) -> int:
    """Guarda una tarea pendiente asociada a una materia existente."""
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO tareas (
                materia_id, titulo, descripcion, vencimiento_utc,
                zona_horaria, tipo_vencimiento, fecha_local
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                materia_id,
                titulo,
                descripcion,
                vencimiento_utc,
                zona_horaria,
                tipo_vencimiento,
                fecha_local,
            ),
        )
        return int(cursor.lastrowid)


def _task_query() -> str:
    return """
        SELECT
            tareas.id,
            tareas.materia_id,
            materias.nombre AS materia_nombre,
            materias.color AS materia_color,
            tareas.titulo,
            tareas.descripcion,
            tareas.vencimiento_utc,
            tareas.zona_horaria,
            tareas.tipo_vencimiento,
            tareas.fecha_local,
            tareas.estado
        FROM tareas
        JOIN materias ON materias.id = tareas.materia_id
    """


def list_tasks(db_path: str | Path) -> list[dict[str, object]]:
    """Lista tareas con nombre y color de materia para mostrarlas."""
    with get_connection(db_path) as connection:
        rows = connection.execute(
            f"{_task_query()} ORDER BY tareas.id"
        ).fetchall()
        return [dict(row) for row in rows]


def get_task(db_path: str | Path, task_id: int) -> dict[str, object] | None:
    """Obtiene una tarea persistida con los datos visibles de su materia."""
    with get_connection(db_path) as connection:
        row = connection.execute(
            f"{_task_query()} WHERE tareas.id = ?",
            (task_id,),
        ).fetchone()
        return dict(row) if row is not None else None
