"""Reglas de vencimiento: normalización a UTC y cálculo de vencida o urgente."""

from datetime import UTC, date, datetime, time, timedelta
import re
from zoneinfo import ZoneInfo

URGENT_WINDOW = timedelta(hours=48)
DATE_ONLY = re.compile(r"\d{4}-\d{2}-\d{2}")


def utc_now() -> datetime:
    """Instante actual en UTC. Las pruebas pueden reemplazarlo."""
    return datetime.now(UTC)


def to_storage(instant: datetime) -> str:
    """Formato fijo en UTC, para que ordenar el texto equivalga a ordenar el tiempo."""
    return instant.astimezone(UTC).isoformat(timespec="microseconds")


def _exists_in_zone(local: datetime, zone: ZoneInfo) -> bool:
    """Una hora local existe si al ir y volver de UTC sigue siendo la misma."""
    back = local.replace(tzinfo=zone).astimezone(UTC).astimezone(zone)
    return back.replace(tzinfo=None) == local


def parse_deadline(value: str, timezone_name: str) -> tuple[datetime, str, date | None]:
    """Valida el vencimiento recibido y devuelve (instante UTC, tipo, fecha local).

    - Solo fecha: vence al inicio exclusivo del día local siguiente.
    - Fecha y hora: debe traer desplazamiento UTC, existir en la zona y coincidir
      con el desplazamiento que la zona tiene en ese momento.

    Lanza ValueError con un mensaje en español si algo no es válido.
    """
    zone = ZoneInfo(timezone_name)

    if DATE_ONLY.fullmatch(value):
        try:
            local_date = date.fromisoformat(value)
        except ValueError as error:
            raise ValueError("La fecha de entrega no es válida.") from error
        next_day = datetime.combine(local_date + timedelta(days=1), time.min)
        # Si la medianoche no existe (cambio de horario), astimezone usa el
        # primer instante real del día siguiente.
        return next_day.replace(tzinfo=zone).astimezone(UTC), "fecha", local_date

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("La fecha de entrega debe usar un formato ISO válido.") from error
    if parsed.utcoffset() is None:
        raise ValueError("La fecha y hora de entrega debe incluir su desplazamiento UTC.")

    local = parsed.replace(tzinfo=None)
    if not _exists_in_zone(local, zone):
        raise ValueError(
            "La hora de entrega no existe en tu zona horaria por un cambio de horario."
        )
    # En horas repetidas (fin del horario de verano) cualquiera de los dos
    # desplazamientos es válido.
    valid_offsets = {local.replace(tzinfo=zone, fold=fold).utcoffset() for fold in (0, 1)}
    if parsed.utcoffset() not in valid_offsets:
        raise ValueError(
            "El desplazamiento UTC de la fecha de entrega no coincide con la zona horaria."
        )
    return parsed.astimezone(UTC), "fecha_hora", None


def classify(deadline_utc: datetime, estado: str, now: datetime) -> tuple[bool, bool]:
    """Devuelve (vencida, urgente). Las tareas completadas no son ninguna de las dos."""
    if estado == "completada":
        return False, False
    if deadline_utc <= now:
        return True, False
    return False, deadline_utc <= now + URGENT_WINDOW
