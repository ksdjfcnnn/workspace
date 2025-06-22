import pytest
from fastapi.testclient import TestClient


def test_create_project_success(client: TestClient, admin_headers):
    """Test successful project creation"""
    project_data = {
        "name": "New Project",
        "description": "A new test project",
        "billable": True
    }
    
    response = client.post(
        "/api/v1/project/",
        json=project_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "A new test project"
    assert data["billable"] is True


def test_create_project_with_employees(client: TestClient, admin_headers, test_user):
    """Test creating project with assigned employees"""
    project_data = {
        "name": "Project with Employees",
        "description": "A project with employees",
        "billable": True,
        "employees": [test_user.id]
    }
    
    response = client.post(
        "/api/v1/project/",
        json=project_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert test_user.id in data["employees"]


def test_get_projects(client: TestClient, admin_headers, test_project):
    """Test getting all projects"""
    response = client.get("/api/v1/project/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_project_by_id(client: TestClient, admin_headers, test_project):
    """Test getting project by ID"""
    response = client.get(f"/api/v1/project/{test_project.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


def test_get_project_not_found(client: TestClient, admin_headers):
    """Test getting non-existent project"""
    response = client.get("/api/v1/project/nonexistent", headers=admin_headers)
    assert response.status_code == 404


def test_update_project(client: TestClient, admin_headers, test_project):
    """Test updating project"""
    update_data = {
        "name": "Updated Project Name",
        "description": "Updated description"
    }
    
    response = client.put(
        f"/api/v1/project/{test_project.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project Name"
    assert data["description"] == "Updated description"


def test_update_project_employees(client: TestClient, admin_headers, test_project, test_user):
    """Test updating project employees"""
    update_data = {
        "employees": [test_user.id]
    }
    
    response = client.put(
        f"/api/v1/project/{test_project.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert test_user.id in data["employees"]


def test_delete_project(client: TestClient, admin_headers, test_project):
    """Test deleting project"""
    response = client.delete(f"/api/v1/project/{test_project.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    
    # Verify project is deleted
    get_response = client.get(f"/api/v1/project/{test_project.id}", headers=admin_headers)
    assert get_response.status_code == 404


def test_delete_project_with_active_shifts(client: TestClient, admin_headers, db, test_project, test_user):
    """Test deleting project with active shifts should fail"""
    from app.models.shift import Shift
    from datetime import datetime
    
    # Create active shift
    shift = Shift(
        type="manual",
        start=int(datetime.utcnow().timestamp() * 1000),
        employeeId=test_user.id,
        organizationId=test_user.organizationId,
        projectId=test_project.id
    )
    db.add(shift)
    db.commit()
    
    response = client.delete(f"/api/v1/project/{test_project.id}", headers=admin_headers)
    assert response.status_code == 400
    assert "active time tracking sessions" in response.json()["detail"]


def test_get_project_stats(client: TestClient, admin_headers, test_project):
    """Test getting project statistics"""
    response = client.get(
        f"/api/v1/project/{test_project.id}/stats",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "totalTimeLogged" in data
    assert "totalEmployees" in data
    assert "totalTasks" in data
    assert "totalScreenshots" in data


def test_unauthorized_project_access(client: TestClient):
    """Test accessing project endpoints without authentication"""
    response = client.get("/api/v1/project/")
    assert response.status_code == 401


def test_user_cannot_access_admin_project_endpoints(client: TestClient, user_headers):
    """Test regular user cannot access admin project endpoints"""
    response = client.post(
        "/api/v1/project/",
        json={"name": "Test", "description": "Test"},
        headers=user_headers
    )
    assert response.status_code == 403