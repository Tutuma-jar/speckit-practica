"""Fixtures compartidas para pruebas aisladas de la aplicación."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    """Proporciona una ruta de base de datos temporal por prueba."""
    return tmp_path / "organizador.sqlite3"


@pytest.fixture
def app(database_path: Path) -> FastAPI:
    """Crea la aplicación usando la base temporal de la prueba."""
    return create_app(database_path)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """Inicia la aplicación y administra el ciclo de vida de TestClient."""
    with TestClient(app) as test_client:
        yield test_client
