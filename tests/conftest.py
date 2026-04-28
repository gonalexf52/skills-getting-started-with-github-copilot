"""
Pytest configuration and fixtures for the FastAPI application tests.
"""
import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of activities data for each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    return deepcopy(activities)


@pytest.fixture
def client(fresh_activities, monkeypatch):
    """
    Provide a TestClient instance with fresh activity data.
    Uses monkeypatch to replace the global activities dict with a fresh copy
    for each test, ensuring complete test isolation.
    """
    # Replace the global activities dict in the app module with a fresh copy
    monkeypatch.setattr("src.app.activities", fresh_activities)
    return TestClient(app)
