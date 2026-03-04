"""
Backend FastAPI tests for app.py using pytest and TestClient.
Tests follow the Arrange-Act-Assert (AAA) pattern.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure src is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_activities(client):
    # Arrange: TestClient fixture
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all("participants" in v for v in data.values())

def test_signup_success(client):
    # Arrange
    activity_name = next(iter(client.get("/activities").json().keys()))
    email = "testuser@example.com"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code in (200, 201)
    data = response.json()
    assert "message" in data
    # Clean up: Remove test user if unregister endpoint exists
    client.post(f"/activities/{activity_name}/unregister?email={email}")

def test_signup_duplicate(client):
    # Arrange
    activity_name = next(iter(client.get("/activities").json().keys()))
    email = "dupeuser@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400 or response.status_code == 409
    data = response.json()
    assert "error" in data or "detail" in data
    # Clean up
    client.post(f"/activities/{activity_name}/unregister?email={email}")

def test_signup_nonexistent_activity(client):
    # Arrange
    activity_name = "nonexistent-activity"
    email = "nobody@example.com"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data

def test_root_redirect(client):
    # Arrange
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (200, 307, 308)
    # Should redirect or serve index.html
