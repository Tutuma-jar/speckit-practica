"""Pruebas de contrato y validación para el registro de materias y tareas."""

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.db import get_connection
from app.main import create_app


def test_list_subjects_starts_empty(client):
    response = client.get("/api/materias")

    assert response.status_code == 200
    assert response.json() == []


def test_app_serves_registration_forms_and_static_assets(client):
    page = client.get("/")
    javascript = client.get("/static/app.js")
    stylesheet = client.get("/static/styles.css")

    assert page.status_code == 200
    assert 'id="subject-form"' in page.text
    assert 'id="task-form"' in page.text
    assert 'for="task-date"' in page.text
    assert javascript.status_code == 200
    assert "textContent" in javascript.text
    assert "innerHTML" not in javascript.text
    assert stylesheet.status_code == 200
    assert "@media (max-width: 42rem)" in stylesheet.text


def test_create_and_list_subject_persists_data(client):
    created = client.post(
        "/api/materias",
        json={"nombre": "Matemáticas", "color": "#3366CC"},
    )

    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        "nombre": "Matemáticas",
        "color": "#3366CC",
    }
    assert client.get("/api/materias").json() == [created.json()]


def test_create_task_and_list_it_with_subject_details(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Matemáticas", "color": "#3366CC"},
    ).json()
    task_data = {
        "materia_id": subject["id"],
        "titulo": "Taller",
        "descripcion": "Resolver ejercicios",
        "vencimiento": "2026-10-27T13:00:00-04:00",
        "zona_horaria": "America/Bogota",
    }

    created = client.post("/api/tareas", json=task_data)

    assert created.status_code == 201
    assert created.json()["materia_id"] == subject["id"]
    assert created.json()["materia_nombre"] == "Matemáticas"
    assert created.json()["materia_color"] == "#3366CC"
    assert created.json()["titulo"] == "Taller"
    assert created.json()["descripcion"] == "Resolver ejercicios"
    assert created.json()["estado"] == "pendiente"
    assert client.get("/api/tareas").json() == [created.json()]


def test_task_creation_rejects_missing_subject(client):
    response = client.post(
        "/api/tareas",
        json={
            "materia_id": 999,
            "titulo": "Taller",
            "vencimiento": "2026-10-27",
            "zona_horaria": "America/Bogota",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["codigo"] == "no_encontrado"


def test_required_fields_are_reported_in_spanish(client):
    missing_subject = client.post(
        "/api/materias",
        json={"color": "#3366CC"},
    )
    missing_task_fields = client.post("/api/tareas", json={})

    assert missing_subject.status_code == 422
    assert missing_subject.json()["error"]["codigo"] == "validacion"
    assert "nombre" in missing_subject.json()["error"]["mensaje"].lower()
    assert missing_task_fields.status_code == 422
    assert missing_task_fields.json()["error"]["codigo"] == "validacion"
    assert "materia" in missing_task_fields.json()["error"]["mensaje"].lower()


def test_subject_name_accepts_one_and_one_hundred_characters(client):
    minimum = client.post(
        "/api/materias",
        json={"nombre": "A", "color": "#123456"},
    )
    maximum = client.post(
        "/api/materias",
        json={"nombre": "M" * 100, "color": "#ABCDEF"},
    )

    assert minimum.status_code == 201
    assert maximum.status_code == 201
    assert len(maximum.json()["nombre"]) == 100


def test_subject_validation_trims_name_and_rejects_invalid_values(client):
    trimmed = client.post(
        "/api/materias",
        json={"nombre": "  Física  ", "color": "#abcdef"},
    )
    blank = client.post(
        "/api/materias",
        json={"nombre": "   ", "color": "#3366CC"},
    )
    too_long = client.post(
        "/api/materias",
        json={"nombre": "N" * 101, "color": "#3366CC"},
    )
    invalid_color = client.post(
        "/api/materias",
        json={"nombre": "Química", "color": "azul"},
    )

    assert trimmed.status_code == 201
    assert trimmed.json()["nombre"] == "Física"
    assert trimmed.json()["color"] == "#abcdef"
    for response in (blank, too_long, invalid_color):
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "validacion"


def test_subjects_with_same_name_have_distinct_ids(client):
    first = client.post(
        "/api/materias",
        json={"nombre": "Física", "color": "#123456"},
    ).json()
    second = client.post(
        "/api/materias",
        json={"nombre": "Física", "color": "#654321"},
    ).json()

    assert first["nombre"] == second["nombre"]
    assert first["id"] != second["id"]


def test_task_title_and_description_accept_exact_maximum_lengths(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Historia", "color": "#123456"},
    ).json()
    response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "T" * 150,
            "descripcion": "D" * 2000,
            "vencimiento": "2026-10-27T13:00:00-04:00",
            "zona_horaria": "America/Bogota",
        },
    )

    assert response.status_code == 201
    assert len(response.json()["titulo"]) == 150
    assert len(response.json()["descripcion"]) == 2000

    minimum_title = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "A",
            "vencimiento": "2026-10-27",
            "zona_horaria": "America/Bogota",
        },
    )
    assert minimum_title.status_code == 201
    assert minimum_title.json()["titulo"] == "A"


def test_task_validation_trims_fields_and_allows_optional_description(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Historia", "color": "#123456"},
    ).json()
    trimmed = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "  Ensayo  ",
            "descripcion": "  Revisar fuentes  ",
            "vencimiento": "2026-10-27T13:00:00-04:00",
            "zona_horaria": "America/Bogota",
        },
    )
    no_description = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Lectura",
            "vencimiento": "2026-10-28",
            "zona_horaria": "America/Bogota",
        },
    )
    blank_description = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Resumen",
            "descripcion": "   ",
            "vencimiento": "2026-10-29",
            "zona_horaria": "America/Bogota",
        },
    )

    assert trimmed.status_code == 201
    assert trimmed.json()["titulo"] == "Ensayo"
    assert trimmed.json()["descripcion"] == "Revisar fuentes"
    assert no_description.status_code == 201
    assert no_description.json()["descripcion"] is None
    assert blank_description.status_code == 201
    assert blank_description.json()["descripcion"] is None
    assert no_description.json()["vencimiento"] == "2026-10-28"


def test_task_validation_rejects_blank_and_overlong_values(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Historia", "color": "#123456"},
    ).json()
    base = {
        "materia_id": subject["id"],
        "titulo": "Taller",
        "vencimiento": "2026-10-27",
        "zona_horaria": "America/Bogota",
    }
    blank_title = client.post(
        "/api/tareas",
        json={**base, "titulo": "   "},
    )
    long_title = client.post(
        "/api/tareas",
        json={**base, "titulo": "T" * 151},
    )
    long_description = client.post(
        "/api/tareas",
        json={**base, "descripcion": "D" * 2001},
    )

    for response in (blank_title, long_title, long_description):
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "validacion"


def test_date_only_deadline_is_saved_at_exclusive_next_local_day(client, database_path):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Geografía", "color": "#123456"},
    ).json()
    response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Mapa",
            "vencimiento": "2026-10-27",
            "zona_horaria": "America/Bogota",
        },
    )

    assert response.status_code == 201
    assert response.json()["vencimiento"] == "2026-10-27"
    with get_connection(database_path) as connection:
        row = connection.execute(
            "SELECT vencimiento_utc, tipo_vencimiento, fecha_local FROM tareas"
        ).fetchone()

    expected = datetime.combine(
        date(2026, 10, 28),
        time.min,
        tzinfo=ZoneInfo("America/Bogota"),
    ).astimezone(timezone.utc)
    assert datetime.fromisoformat(row["vencimiento_utc"]) == expected
    assert row["tipo_vencimiento"] == "fecha"
    assert row["fecha_local"] == "2026-10-27"


def test_application_keeps_subject_and_task_after_restart(client, database_path):
    subject_response = client.post(
        "/api/materias",
        json={"nombre": "Biología", "color": "#3366CC"},
    )
    assert subject_response.status_code == 201
    subject = subject_response.json()
    task_response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Informe",
            "vencimiento": "2026-10-27",
            "zona_horaria": "America/Bogota",
        },
    )
    assert task_response.status_code == 201
    task = task_response.json()

    with TestClient(create_app(database_path)) as restarted_client:
        assert restarted_client.get("/api/materias").json() == [subject]
        assert restarted_client.get("/api/tareas").json() == [task]


def test_task_list_sorts_by_deadline_then_id_stably(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "CÃ¡lculo", "color": "#3366CC"},
    ).json()
    later = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Posterior",
            "vencimiento": "2026-10-28T10:00:00+00:00",
            "zona_horaria": "Etc/UTC",
        },
    )
    first_tie = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Empate A",
            "vencimiento": "2026-10-27T10:00:00+00:00",
            "zona_horaria": "Etc/UTC",
        },
    )
    second_tie = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Empate B",
            "vencimiento": "2026-10-27T10:00:00+00:00",
            "zona_horaria": "Etc/UTC",
        },
    )

    assert all(
        response.status_code == 201
        for response in (later, first_tie, second_tie)
    )
    expected_ids = [
        first_tie.json()["id"],
        second_tie.json()["id"],
        later.json()["id"],
    ]
    first_result = [task["id"] for task in client.get("/api/tareas").json()]
    second_result = [task["id"] for task in client.get("/api/tareas").json()]

    assert first_result == expected_ids
    assert second_result == expected_ids


def test_task_accepts_explicit_utc_offset(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "FÃ­sica", "color": "#3366CC"},
    ).json()

    response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "PrÃ¡ctica",
            "vencimiento": "2026-10-27T13:00:00+00:00",
            "zona_horaria": "Etc/UTC",
        },
    )

    assert response.status_code == 201
    assert response.json()["vencimiento"] == "2026-10-27T13:00:00+00:00"


def test_task_accepts_iana_timezone_and_matching_offset(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "GeografÃ­a", "color": "#3366CC"},
    ).json()

    response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Mapa",
            "vencimiento": "2026-10-27T08:30:00+09:00",
            "zona_horaria": "Asia/Tokyo",
        },
    )

    assert response.status_code == 201
    assert response.json()["vencimiento"] == "2026-10-27T08:30:00+09:00"


def test_task_rejects_nonexistent_local_time_in_iana_timezone(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Historia", "color": "#3366CC"},
    ).json()

    response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Lectura",
            # New York skips from 01:59:59 to 03:00:00 on this date.
            "vencimiento": "2026-03-08T02:30:00-05:00",
            "zona_horaria": "America/New_York",
        },
    )

    assert response.status_code == 422


def test_task_rejects_offset_inconsistent_with_iana_timezone(client):
    subject = client.post(
        "/api/materias",
        json={"nombre": "Literatura", "color": "#3366CC"},
    ).json()

    response = client.post(
        "/api/tareas",
        json={
            "materia_id": subject["id"],
            "titulo": "Ensayo",
            # New York is UTC-05:00 in January, not UTC-04:00.
            "vencimiento": "2026-01-15T12:00:00-04:00",
            "zona_horaria": "America/New_York",
        },
    )

    assert response.status_code == 422
