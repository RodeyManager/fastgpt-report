"""Shared test fixtures for knowledge-process-api."""

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)
