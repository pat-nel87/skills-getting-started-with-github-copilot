import src.app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange
    root_path = "/"

    # Act
    response = client.get(root_path, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    # Arrange
    activities_path = "/activities"

    # Act
    response = client.get(activities_path)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert {"description", "schedule", "max_participants", "participants"}.issubset(payload["Chess Club"].keys())
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_adds_participant_successfully(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]
    assert len(app_module.activities[activity_name]["participants"]) == before_count + 1


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    missing_activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{missing_activity}/signup", params={"email": "student@mergington.edu"})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant_case_insensitive(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]
    mixed_case_email = f"  {existing_email.upper()}  "

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": mixed_case_email},
    )
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Removed {mixed_case_email} from {activity_name}"
    assert all(
        participant.strip().lower() != existing_email.strip().lower()
        for participant in app_module.activities[activity_name]["participants"]
    )


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    missing_activity = "Nonexistent Club"

    # Act
    response = client.delete(
        f"/activities/{missing_activity}/participants",
        params={"email": "student@mergington.edu"},
    )
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_unregister_returns_404_when_participant_missing(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Participant not found in activity"
