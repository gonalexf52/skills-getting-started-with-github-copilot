"""
Integration tests for the FastAPI activities application.
Tests follow the Arrange-Act-Assert (AAA) pattern for clarity and structure.
"""
import pytest


# ============================================================================
# GET /activities Tests
# ============================================================================


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test: GET /activities returns all activities with 200 status.
        
        Arrange: HTTP client is ready
        Act: Make GET request to /activities
        Assert: Response is 200 and contains all expected activities
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Drama Club",
            "Science Club",
            "Debate Team"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_has_correct_structure(self, client):
        """
        Test: Each activity has all required fields in correct format.
        
        Arrange: HTTP client is ready
        Act: Make GET request to /activities
        Assert: Each activity contains description, schedule, max_participants, participants
        """
        # Arrange
        required_fields = {
            "description": str,
            "schedule": str,
            "max_participants": int,
            "participants": list
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_details in activities.items():
            for field_name, field_type in required_fields.items():
                assert field_name in activity_details, \
                    f"Activity '{activity_name}' missing field '{field_name}'"
                assert isinstance(activity_details[field_name], field_type), \
                    f"Field '{field_name}' in '{activity_name}' should be {field_type.__name__}"


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """
        Test: New participant can successfully sign up for an activity.
        
        Arrange: Select an activity and an email that's not yet registered
        Act: Make POST request to signup endpoint
        Assert: Status is 200 and participant is added to the activity
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_already_registered_returns_400(self, client):
        """
        Test: Attempting to signup an already-registered participant returns 400.
        
        Arrange: Select an activity and a participant already in it (Chess Club has michael@)
        Act: Make POST request to signup with already-registered email
        Assert: Status is 400 and appropriate error message returned
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test: Attempting to signup for non-existent activity returns 404.
        
        Arrange: Use an invalid activity name
        Act: Make POST request to signup for non-existent activity
        Assert: Status is 404 and appropriate error message returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_signup_increases_participant_count(self, client):
        """
        Test: Signing up a participant increases the participant count.
        
        Arrange: Get initial participant count for an activity
        Act: Sign up a new participant
        Assert: Participant count increased by 1
        """
        # Arrange
        activity_name = "Swimming Club"
        email = "newswimmer@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity_name]["participants"])
        assert updated_count == initial_count + 1


# ============================================================================
# POST /activities/{activity_name}/unregister Tests
# ============================================================================


class TestUnregister:
    """Test suite for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_participant_success(self, client):
        """
        Test: A registered participant can successfully unregister.
        
        Arrange: Select an activity and a participant in it (Chess Club has michael@)
        Act: Make POST request to unregister endpoint
        Assert: Status is 200 and participant is removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered_returns_400(self, client):
        """
        Test: Attempting to unregister a non-registered participant returns 400.
        
        Arrange: Use an email not registered for an activity
        Act: Make POST request to unregister with unregistered email
        Assert: Status is 400 and appropriate error message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test: Attempting to unregister from non-existent activity returns 404.
        
        Arrange: Use an invalid activity name
        Act: Make POST request to unregister from non-existent activity
        Assert: Status is 404 and appropriate error message returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_unregister_decreases_participant_count(self, client):
        """
        Test: Unregistering a participant decreases the participant count.
        
        Arrange: Get initial participant count for an activity
        Act: Unregister a participant
        Assert: Participant count decreased by 1
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity_name]["participants"])
        assert updated_count == initial_count - 1


# ============================================================================
# Integration Tests - Multi-step workflows
# ============================================================================


class TestIntegrationWorkflows:
    """Integration tests for multi-step workflows."""

    def test_signup_and_unregister_workflow(self, client):
        """
        Test: Full workflow of signing up and then unregistering.
        
        Arrange: Select activity and email
        Act: Sign up participant, then unregister same participant
        Assert: Participant is added then removed successfully
        """
        # Arrange
        activity_name = "Art Club"
        email = "artist@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert - Signup successful
        assert signup_response.status_code == 200
        after_signup = client.get("/activities").json()
        assert email in after_signup[activity_name]["participants"]
        assert len(after_signup[activity_name]["participants"]) == initial_count + 1

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        after_unregister = client.get("/activities").json()
        assert email not in after_unregister[activity_name]["participants"]
        assert len(after_unregister[activity_name]["participants"]) == initial_count

    def test_multiple_participants_signup_workflow(self, client):
        """
        Test: Multiple participants can sign up for the same activity.
        
        Arrange: Select activity and multiple emails
        Act: Sign up multiple participants
        Assert: All participants are added to the activity
        """
        # Arrange
        activity_name = "Drama Club"
        emails = [
            "actor1@mergington.edu",
            "actor2@mergington.edu",
            "actor3@mergington.edu"
        ]
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # Assert
        final_activities = client.get("/activities").json()
        assert len(final_activities[activity_name]["participants"]) == initial_count + len(emails)
        for email in emails:
            assert email in final_activities[activity_name]["participants"]
