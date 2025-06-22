import pytest
from fastapi.testclient import TestClient


def test_get_current_user_profile(client: TestClient, user_headers, test_user):
    """Test getting current user profile"""
    response = client.get("/api/v1/user/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


def test_get_current_user_stats(client: TestClient, user_headers, test_user):
    """Test getting current user statistics"""
    response = client.get("/api/v1/user/me/stats", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "totalTimeLogged" in data
    assert "totalProjects" in data
    assert "totalTasks" in data
    assert "totalScreenshots" in data
    assert "activeShifts" in data
    assert "weeklyTimeLogged" in data
    assert "monthlyTimeLogged" in data


def test_get_user_projects(client: TestClient, user_headers, db, test_user, test_project):
    """Test getting user's assigned projects"""
    # Assign user to project
    test_project.employees.append(test_user)
    db.commit()
    
    response = client.get("/api/v1/user/projects/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(project["id"] == test_project.id for project in data)


def test_get_user_project_by_id(client: TestClient, user_headers, db, test_user, test_project):
    """Test getting specific user project"""
    # Assign user to project
    test_project.employees.append(test_user)
    db.commit()
    
    response = client.get(f"/api/v1/user/projects/{test_project.id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


def test_get_unassigned_project(client: TestClient, user_headers, test_project):
    """Test getting project user is not assigned to"""
    response = client.get(f"/api/v1/user/projects/{test_project.id}", headers=user_headers)
    assert response.status_code == 404


def test_get_user_tasks(client: TestClient, user_headers, db, test_user, test_task):
    """Test getting user's assigned tasks"""
    # Assign user to task
    test_task.employees.append(test_user)
    db.commit()
    
    response = client.get("/api/v1/user/tasks/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(task["id"] == test_task.id for task in data)


def test_get_user_task_by_id(client: TestClient, user_headers, db, test_user, test_task):
    """Test getting specific user task"""
    # Assign user to task
    test_task.employees.append(test_user)
    db.commit()
    
    response = client.get(f"/api/v1/user/tasks/{test_task.id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_task.id
    assert data["name"] == test_task.name


def test_get_unassigned_task(client: TestClient, user_headers, test_task):
    """Test getting task user is not assigned to"""
    response = client.get(f"/api/v1/user/tasks/{test_task.id}", headers=user_headers)
    assert response.status_code == 404


def test_unauthorized_profile_access(client: TestClient):
    """Test accessing profile endpoints without authentication"""
    response = client.get("/api/v1/user/me")
    assert response.status_code == 401