from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data():
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["student@mergington.edu"],
        }
    }


@pytest.fixture
def client(monkeypatch, activity_data):
    monkeypatch.setattr(app_module, "activities", activity_data)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, activity_data):
    # Arrange
    expected_activities = activity_data

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_data):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activity_data["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activity_data):
    # Arrange
    email = "student@mergington.edu"
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client, activity_data):
    # Arrange
    email = "newstudent@mergington.edu"
    original_activities = deepcopy(activity_data)

    # Act
    response = client.post("/activities/Robotics/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_data == original_activities


def test_unregister_removes_participant(client, activity_data):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activity_data["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client, activity_data):
    # Arrange
    email = "student@mergington.edu"
    original_activities = deepcopy(activity_data)

    # Act
    response = client.delete("/activities/Robotics/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_data == original_activities


def test_unregister_rejects_nonparticipant(client, activity_data):
    # Arrange
    email = "not-signed-up@mergington.edu"
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == original_participants
