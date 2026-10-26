"""Creación de la aplicación FastAPI y entrega de recursos estáticos."""

from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import db, deadlines, schemas

STATIC_DIR = Path(__file__).parent / "static"
FIELD_NAMES = {
    "nombre": "nombre",
    "color": "color",
    "materia_id": "materia",
    "titulo": "título",
    "descripcion": "descripción",
    "vencimiento": "fecha de entrega",
    "zona_horaria": "zona horaria",
}
FIELD_LIMITS = {
    "nombre": 100,
    "titulo": 150,
    "descripcion": 2000,
}


def _validation_message(error: RequestValidationError) -> str:
    """Traduce los errores de validación del esquema a mensajes en español."""
    details = error.errors()
    if not details:
        return "La solicitud no contiene datos válidos."

    first_error = details[0]
    field = str(first_error["loc"][-1]) if first_error["loc"] else "solicitud"
    field_name = FIELD_NAMES.get(field, "solicitud")
    error_type = str(first_error["type"])

    if error_type == "missing":
        return f"Falta el campo obligatorio «{field_name}»."
    if error_type in {"string_too_long", "too_long"} and field in FIELD_LIMITS:
        return (
            f"El campo «{field_name}» no puede superar "
            f"{FIELD_LIMITS[field]} caracteres."
        )
    if error_type in {"string_too_short", "too_short"}:
        return f"El campo «{field_name}» no puede quedar vacío."
    if error_type == "value_error" and field not in FIELD_NAMES:
        # Error entre campos (fecha con su zona): su ubicación es solo ("body",)
        # y el mensaje en español viene en el propio ValueError.
        cause = first_error.get("ctx", {}).get("error")
        return str(cause) if cause else "La fecha de entrega no es válida."
    if field == "color":
        return "El color debe tener el formato hexadecimal #RRGGBB."
    if field == "vencimiento":
        return "La fecha de entrega debe ser una fecha ISO válida."
    if field == "zona_horaria":
        return "La zona horaria debe ser un identificador IANA válido."
    return f"El campo «{field_name}» no es válido."


def create_app(
    db_path: str | Path | None = None,
    clock: Callable[[], datetime] | None = None,
) -> FastAPI:
    """Crea la aplicación y permite aislar su base de datos y su reloj en pruebas."""
    resolved_db_path = db.get_database_path(db_path)

    def now_utc() -> datetime:
        # Se busca deadlines.utc_now al llamar, para que las pruebas puedan
        # reemplazarlo con monkeypatch además de pasar `clock`.
        return (clock or deadlines.utc_now)()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        db.init_db(resolved_db_path)
        yield

    application = FastAPI(
        title="Organizador de tareas académicas UPB",
        lifespan=lifespan,
    )
    application.state.db_path = resolved_db_path
    application.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR),
        name="static",
    )

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "codigo": "validacion",
                    "mensaje": _validation_message(error),
                }
            },
        )

    @application.exception_handler(HTTPException)
    async def handle_http_error(
        _: Request,
        error: HTTPException,
    ) -> JSONResponse:
        code = "no_encontrado" if error.status_code == 404 else "conflicto"
        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": {
                    "codigo": code,
                    "mensaje": str(error.detail),
                }
            },
            headers=error.headers,
        )

    @application.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @application.get(
        "/api/materias",
        response_model=list[schemas.SubjectResponse],
    )
    async def get_subjects() -> list[dict[str, int | str]]:
        return db.list_subjects(resolved_db_path)

    @application.post(
        "/api/materias",
        response_model=schemas.SubjectResponse,
        status_code=201,
    )
    async def post_subject(
        subject: schemas.SubjectCreate,
    ) -> dict[str, int | str]:
        return db.create_subject(
            resolved_db_path,
            subject.nombre,
            subject.color,
        )

    @application.get(
        "/api/tareas",
        response_model=list[schemas.TaskResponse],
    )
    async def get_tasks() -> list[schemas.TaskResponse]:
        # Un solo instante por respuesta: todas las tareas se clasifican igual.
        now = now_utc()
        return [
            schemas.present_task(task, now)
            for task in db.list_tasks(resolved_db_path)
        ]

    @application.post(
        "/api/tareas",
        response_model=schemas.TaskResponse,
        status_code=201,
    )
    async def post_task(task: schemas.TaskCreate) -> schemas.TaskResponse:
        if not db.subject_exists(resolved_db_path, task.materia_id):
            raise HTTPException(
                status_code=404,
                detail="La materia indicada no existe.",
            )
        deadline_utc, deadline_type, local_date = deadlines.parse_deadline(
            task.vencimiento,
            task.zona_horaria,
        )
        task_id = db.create_task(
            resolved_db_path,
            materia_id=task.materia_id,
            titulo=task.titulo,
            descripcion=task.descripcion,
            vencimiento_utc=deadlines.to_storage(deadline_utc),
            zona_horaria=task.zona_horaria,
            tipo_vencimiento=deadline_type,
            fecha_local=local_date.isoformat() if local_date else None,
        )
        saved_task = db.get_task(resolved_db_path, task_id)
        if saved_task is None:
            raise RuntimeError("La tarea creada no apareció en la base de datos.")
        return schemas.present_task(saved_task, now_utc())

    return application


app = create_app()
