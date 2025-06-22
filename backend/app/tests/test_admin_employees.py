import pytest
from fastapi.testclient import TestClient


def test_create_employee_success(client: TestClient, admin_headers, test_organization):
    """Test successful employee creation"""
    employee_data = {
        "name": "New Employee",
        "email": "newemployee@test.com",
        "title": "Developer",
        "type": "personal"
    }
    
    response = client.post(
        "/api/v1/employee/",
        json=employee_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Employee"
    assert data["email"] == "newemployee@test.com"
    assert data["organizationId"] == test_organization.id


def test_create_employee_duplicate_email(client: TestClient, admin_headers, test_user):
    """Test creating employee with duplicate email"""
    employee_data = {
        "name": "Duplicate User",
        "email": "user@test.com",  # Same as test_user
        "title": "Developer",
        "type": "personal"
    }
    
    response = client.post(
        "/api/v1/employee/",
        json=employee_data,
        headers=admin_headers
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_employee_unauthorized(client: TestClient, user_headers):
    """Test creating employee without admin privileges"""
    employee_data = {
        "name": "New Employee",
        "email": "newemployee@test.com",
        "title": "Developer",
        "type": "personal"
    }
    
    response = client.post(
        "/api/v1/employee/",
        json=employee_data,
        headers=user_headers
    )
    assert response.status_code == 403


def test_get_employees(client: TestClient, admin_headers, test_user):
    """Test getting all employees"""
    response = client.get("/api/v1/employee/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least test_user should be present


def test_get_employee_by_id(client: TestClient, admin_headers, test_user):
    """Test getting employee by ID"""
    response = client.get(f"/api/v1/employee/{test_user.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_employee_not_found(client: TestClient, admin_headers):
    """Test getting non-existent employee"""
    response = client.get("/api/v1/employee/nonexistent", headers=admin_headers)
    assert response.status_code == 404


def test_update_employee(client: TestClient, admin_headers, test_user):
    """Test updating employee"""
    update_data = {
        "name": "Updated Name",
        "title": "Senior Developer"
    }
    
    response = client.put(
        f"/api/v1/employee/{test_user.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["title"] == "Senior Developer"


def test_deactivate_employee(client: TestClient, admin_headers, test_user):
    """Test deactivating employee"""
    response = client.post(
        f"/api/v1/employee/deactivate/{test_user.id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["deactivated"] is not None


def test_deactivate_employee_already_deactivated(client: TestClient, admin_headers, db, test_user):
    """Test deactivating already deactivated employee"""
    # First deactivate
    test_user.deactivated = 1234567890000
    db.commit()
    
    response = client.post(
        f"/api/v1/employee/deactivate/{test_user.id}",
        headers=admin_headers
    )
    assert response.status_code == 409
    assert "already deactivated" in response.json()["detail"]


def test_deactivate_self(client: TestClient, admin_headers, test_admin_user):
    """Test admin cannot deactivate themselves"""
    response = client.post(
        f"/api/v1/employee/deactivate/{test_admin_user.id}",
        headers=admin_headers
    )
    assert response.status_code == 400
    assert "Cannot deactivate yourself" in response.json()["detail"]


def test_activate_employee(client: TestClient, admin_headers, db, test_user):
    """Test activating deactivated employee"""
    # First deactivate
    test_user.deactivated = 1234567890000
    db.commit()
    
    response = client.post(
        f"/api/v1/employee/activate/{test_user.id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["deactivated"] is None


def test_get_employee_stats(client: TestClient, admin_headers, test_user):
    """Test getting employee statistics"""
    response = client.get(
        f"/api/v1/employee/{test_user.id}/stats",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "totalTimeLogged" in data
    assert "totalProjects" in data
    assert "totalTasks" in data
    assert "totalScreenshots" in data


def test_unauthorized_access(client: TestClient):
    """Test accessing employee endpoints without authentication"""
    response = client.get("/api/v1/employee/")
    assert response.status_code == 401


def test_user_cannot_access_admin_endpoints(client: TestClient, user_headers):
    """Test regular user cannot access admin employee endpoints"""
    response = client.get("/api/v1/employee/", headers=user_headers)
    assert response.status_code == 403