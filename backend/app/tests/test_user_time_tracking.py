import pytest
from fastapi.testclient import TestClient
from datetime import datetime


def test_start_time_tracking_success(client: TestClient, user_headers, test_project, test_task, db, test_user):
    """Test successful time tracking start"""
    # Assign user to project and task
    test_project.employees.append(test_user)
    test_task.employees.append(test_user)
    db.commit()
    
    shift_data = {
        "name": "Working on feature",
        "projectId": test_project.id,
        "taskId": test_task.id,
        "timezoneOffset": -18000000  # -5 hours in milliseconds
    }
    
    response = client.post(
        "/api/v1/user/time-tracking/start",
        json=shift_data,
        headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Working on feature"
    assert data["projectId"] == test_project.id
    assert data["taskId"] == test_task.id
    assert data["end"] is None  # Should be active


def test_start_time_tracking_unassigned_project(client: TestClient, user_headers, test_project):
    """Test starting time tracking on unassigned project"""
    shift_data = {
        "name": "Working on feature",
        "projectId": test_project.id
    }
    
    response = client.post(
        "/api/v1/user/time-tracking/start",
        json=shift_data,
        headers=user_headers
    )
    assert response.status_code == 400
    assert "not assigned to this project" in response.json()["detail"]


def test_start_time_tracking_unassigned_task(client: TestClient, user_headers, test_task):
    """Test starting time tracking on unassigned task"""
    shift_data = {
        "name": "Working on feature",
        "taskId": test_task.id
    }
    
    response = client.post(
        "/api/v1/user/time-tracking/start",
        json=shift_data,
        headers=user_headers
    )
    assert response.status_code == 400
    assert "not assigned to this task" in response.json()["detail"]


def test_start_time_tracking_already_active(client: TestClient, user_headers, db, test_user):
    """Test starting time tracking when already active"""
    from app.models.shift import Shift
    
    # Create active shift
    active_shift = Shift(
        type="manual",
        start=int(datetime.utcnow().timestamp() * 1000),
        employeeId=test_user.id,
        organizationId=test_user.organizationId,
        name="Existing shift"
    )
    db.add(active_shift)
    db.commit()
    
    shift_data = {
        "name": "New shift"
    }
    
    response = client.post(
        "/api/v1/user/time-tracking/start",
        json=shift_data,
        headers=user_headers
    )
    assert response.status_code == 400
    assert "already has an active shift" in response.json()["detail"]


def test_end_time_tracking_success(client: TestClient, user_headers, db, test_user):
    """Test successful time tracking end"""
    from app.models.shift import Shift
    
    # Create active shift
    active_shift = Shift(
        type="manual",
        start=int(datetime.utcnow().timestamp() * 1000),
        employeeId=test_user.id,
        organizationId=test_user.organizationId,
        name="Active shift"
    )
    db.add(active_shift)
    db.commit()
    
    response = client.post(
        "/api/v1/user/time-tracking/end",
        headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["end"] is not None
    assert data["id"] == active_shift.id


def test_end_time_tracking_no_active_shift(client: TestClient, user_headers):
    """Test ending time tracking with no active shift"""
    response = client.post(
        "/api/v1/user/time-tracking/end",
        headers=user_headers
    )
    assert response.status_code == 400
    assert "No active time tracking session" in response.json()["detail"]


def test_get_active_shift(client: TestClient, user_headers, db, test_user):
    """Test getting active shift"""
    from app.models.shift import Shift
    
    # Create active shift
    active_shift = Shift(
        type="manual",
        start=int(datetime.utcnow().timestamp() * 1000),
        employeeId=test_user.id,
        organizationId=test_user.organizationId,
        name="Active shift"
    )
    db.add(active_shift)
    db.commit()
    
    response = client.get(
        "/api/v1/user/time-tracking/active",
        headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == active_shift.id
    assert data["end"] is None


def test_get_active_shift_none(client: TestClient, user_headers):
    """Test getting active shift when none exists"""
    response = client.get(
        "/api/v1/user/time-tracking/active",
        headers=user_headers
    )
    assert response.status_code == 404
    assert "No active time tracking session" in response.json()["detail"]


def test_get_time_tracking_history(client: TestClient, user_headers, db, test_user):
    """Test getting time tracking history"""
    from app.models.shift import Shift
    
    # Create completed shift
    completed_shift = Shift(
        type="manual",
        start=int(datetime.utcnow().timestamp() * 1000) - 3600000,  # 1 hour ago
        end=int(datetime.utcnow().timestamp() * 1000),
        employeeId=test_user.id,
        organizationId=test_user.organizationId,
        name="Completed shift"
    )
    db.add(completed_shift)
    db.commit()
    
    response = client.get(
        "/api/v1/user/time-tracking/history",
        headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == completed_shift.id


def test_get_time_tracking_history_with_filters(client: TestClient, user_headers, db, test_user, test_project):
    """Test getting time tracking history with filters"""
    from app.models.shift import Shift
    
    # Create shift with project
    shift_with_project = Shift(
        type="manual",
        start=int(datetime.utcnow().timestamp() * 1000) - 3600000,
        end=int(datetime.utcnow().timestamp() * 1000),
        employeeId=test_user.id,
        organizationId=test_user.organizationId,
        projectId=test_project.id,
        name="Project shift"
    )
    db.add(shift_with_project)
    db.commit()
    
    response = client.get(
        f"/api/v1/user/time-tracking/history?project_id={test_project.id}",
        headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(shift["projectId"] == test_project.id for shift in data if shift["projectId"])


def test_unauthorized_time_tracking_access(client: TestClient):
    """Test accessing time tracking endpoints without authentication"""
    response = client.post("/api/v1/user/time-tracking/start", json={"name": "Test"})
    assert response.status_code == 401