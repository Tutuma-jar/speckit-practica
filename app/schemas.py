"""Modelos y validación de los datos recibidos y devueltos por la API."""

from datetime import UTC, date, datetime, time, timedelta
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectCreate(BaseModel):
    """Datos obligatorios para registrar una materia."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=100)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class SubjectResponse(BaseModel):
    """Materia almacenada."""

    id: int
    nombre: str
    color: str


class TaskCreate(BaseModel):
    """Datos para registrar una tarea con vencimiento local explícito."""

    model_config = ConfigDict(str_strip_whitespace=True)

    materia_id: int = Field(gt=0)
    titulo: str = Field(min_length=1, max_length=150)
    descripcion: str | None = Field(default=None, max_length=2000)
    vencimiento: str
    zona_horaria: str

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @field_validator("vencimiento")
    @classmethod
    def validate_deadline_format(cls, value: str) -> str:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            try:
                date.fromisoformat(value)
            except ValueError as error:
                raise ValueError("La fecha de entrega no es válida.") from error
            return value

        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                "La fecha de entrega debe usar un formato ISO válido."
            ) from error
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError(
                "La fecha y hora de entrega debe incluir su desplazamiento UTC."
            )
        return value

    @field_validator("zona_horaria")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise ValueError("La zona horaria IANA no es válida.") from error
        return value


class TaskResponse(BaseModel):
    """Tarea guardada con los datos visibles de su materia."""

    id: int
    materia_id: int
    materia_nombre: str
    materia_color: str
    titulo: str
    descripcion: str | None
    vencimiento: str
    estado: str


def normalize_deadline(
    deadline: str,
    timezone_name: str,
) -> tuple[str, str, str | None]:
    """Convierte el vencimiento a UTC y conserva el formato local ingresado."""
    zone = ZoneInfo(timezone_name)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
        local_date = date.fromisoformat(deadline)
        exclusive_end = datetime.combine(
            local_date + timedelta(days=1),
            time.min,
            tzinfo=zone,
        )
        utc_deadline = exclusive_end.astimezone(UTC)
        return (
            utc_deadline.isoformat(timespec="microseconds"),
            "fecha",
            local_date.isoformat(),
        )

    local_deadline = datetime.fromisoformat(deadline)
    utc_deadline = local_deadline.astimezone(UTC)
    return utc_deadline.isoformat(timespec="microseconds"), "fecha_hora", None


def present_task(row: dict[str, object]) -> TaskResponse:
    """Transforma una fila SQLite en la forma pública de una tarea."""
    if row["tipo_vencimiento"] == "fecha":
        deadline = str(row["fecha_local"])
    else:
        utc_deadline = datetime.fromisoformat(str(row["vencimiento_utc"]))
        local_deadline = utc_deadline.astimezone(ZoneInfo(str(row["zona_horaria"])))
        deadline = local_deadline.isoformat(timespec="seconds")

    return TaskResponse(
        id=int(row["id"]),
        materia_id=int(row["materia_id"]),
        materia_nombre=str(row["materia_nombre"]),
        materia_color=str(row["materia_color"]),
        titulo=str(row["titulo"]),
        descripcion=(
            str(row["descripcion"])
            if row["descripcion"] is not None
            else None
        ),
        vencimiento=deadline,
        estado=str(row["estado"]),
    )
