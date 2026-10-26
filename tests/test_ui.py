"""Pruebas de accesibilidad para la interfaz del organizador."""

import json
from pathlib import Path

import pytest
from playwright.sync_api import Page, Route

STATIC_DIR = Path(__file__).parents[1] / "app" / "static"


@pytest.fixture
def application_page(page: Page) -> Page:
    subjects = [{"id": 1, "nombre": "Cálculo I", "color": "#3366cc"}]

    def fulfill_subjects(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(subjects),
        )

    def fulfill_tasks(route: Route) -> None:
        route.fulfill(status=200, content_type="application/json", body="[]")

    page.route("**/api/materias", fulfill_subjects)
    page.route("**/api/tareas", fulfill_tasks)

    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    html = html.replace("<head>", '<head><base href="http://organizador.test/">')
    html = html.replace('    <script src="/static/app.js" defer></script>\n', "")
    page.set_content(html)
    page.add_script_tag(path=str(STATIC_DIR / "app.js"))
    page.locator("#subject-list .subject-name").wait_for()
    return page


def test_primary_controls_have_accessible_labels(application_page: Page) -> None:
    for label in (
        "Nombre de la materia",
        "Color de la materia",
        "Materia",
        "Título",
        "Descripción (opcional)",
        "Fecha de entrega",
        "Hora de entrega (opcional)",
    ):
        assert application_page.get_by_label(label).is_visible()


def test_primary_controls_are_reachable_by_keyboard(application_page: Page) -> None:
    page = application_page
    page.locator("#subject-name").focus()

    for selector in (
        "#subject-color",
        "#subject-form button[type='submit']",
        "#task-subject",
        "#task-title",
        "#task-description",
        "#task-date",
        "#task-time",
        "#task-submit",
    ):
        page.keyboard.press("Tab")
        assert page.locator(selector).evaluate(
            "(element) => element === document.activeElement"
        )


def test_subject_name_is_identified_in_text_without_relying_on_color(
    application_page: Page,
) -> None:
    assert (
        application_page.locator("#subject-list .subject-name").inner_text()
        == "Cálculo I"
    )
    assert (
        application_page.locator("#task-subject option").nth(1).inner_text()
        == "Cálculo I (#3366cc)"
    )
