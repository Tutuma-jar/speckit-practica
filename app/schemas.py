"""Modelos y validación de los datos recibidos y devueltos por la API."""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app import deadlines


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

    @field_validator("zona_horaria")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise ValueError("La zona horaria IANA no es válida.") from error
        return value

    @model_validator(mode="after")
    def validate_deadline(self) -> "TaskCreate":
        # Se valida junto con la zona: una hora puede no existir o no coincidir
        # con el desplazamiento de esa zona.
        deadlines.parse_deadline(self.vencimiento, self.zona_horaria)
        return self


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
    vencida: bool
    urgente: bool


def present_task(row: dict[str, object], now: datetime) -> TaskResponse:
    """Transforma una fila SQLite en la forma pública de una tarea.

    `now` es el instante UTC único de la respuesta, para que todas las tareas
    de un mismo listado se clasifiquen contra el mismo momento.
    """
    utc_deadline = datetime.fromisoformat(str(row["vencimiento_utc"]))
    if row["tipo_vencimiento"] == "fecha":
        deadline = str(row["fecha_local"])
    else:
        local_deadline = utc_deadline.astimezone(ZoneInfo(str(row["zona_horaria"])))
        deadline = local_deadline.isoformat(timespec="seconds")
    vencida, urgente = deadlines.classify(utc_deadline, str(row["estado"]), now)

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
        vencida=vencida,
        urgente=urgente,
    )
