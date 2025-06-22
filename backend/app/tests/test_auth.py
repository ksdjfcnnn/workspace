import pytest
from fastapi.testclient import TestClient
from app.core.security import create_email_verification_token


def test_login_success(client: TestClient, test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client: TestClient):
    """Test login with invalid email"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@test.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_invalid_password(client: TestClient, test_user):
    """Test login with invalid password"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_unverified_email(client: TestClient, db, test_organization, test_team):
    """Test login with unverified email"""
    from app.models.employee import Employee
    from app.core.security import get_password_hash
    
    unverified_user = Employee(
        name="Unverified User",
        email="unverified@test.com",
        password_hash=get_password_hash("password123"),
        organizationId=test_organization.id,
        teamId=test_team.id,
        emailVerified=False
    )
    db.add(unverified_user)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@test.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert "Email not verified" in response.json()["detail"]


def test_login_deactivated_user(client: TestClient, db, test_user):
    """Test login with deactivated user"""
    test_user.deactivated = 1234567890000
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert "Account is deactivated" in response.json()["detail"]


def test_verify_email_success(client: TestClient, db, test_organization, test_team):
    """Test successful email verification"""
    from app.models.employee import Employee
    
    # Create unverified user
    user = Employee(
        name="New User",
        email="new@test.com",
        organizationId=test_organization.id,
        teamId=test_team.id,
        emailVerified=False,
        invited=1234567890000
    )
    db.add(user)
    db.commit()
    
    # Create verification token
    token = create_email_verification_token("new@test.com")
    
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": token, "password": "newpassword123"}
    )
    assert response.status_code == 200
    assert "Email verified and password set successfully" in response.json()["message"]
    
    # Verify user can now login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "new@test.com", "password": "newpassword123"}
    )
    assert login_response.status_code == 200


def test_verify_email_invalid_token(client: TestClient):
    """Test email verification with invalid token"""
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": "invalid_token", "password": "newpassword123"}
    )
    assert response.status_code == 400
    assert "Invalid or expired verification token" in response.json()["detail"]


def test_forgot_password(client: TestClient, test_user):
    """Test forgot password request"""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "user@test.com"}
    )
    assert response.status_code == 200
    assert "password reset link has been sent" in response.json()["message"]


def test_forgot_password_nonexistent_email(client: TestClient):
    """Test forgot password with non-existent email"""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@test.com"}
    )
    assert response.status_code == 200  # Don't reveal if email exists
    assert "password reset link has been sent" in response.json()["message"]


def test_reset_password_success(client: TestClient, test_user):
    """Test successful password reset"""
    token = create_email_verification_token("user@test.com")
    
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "password": "newpassword123"}
    )
    assert response.status_code == 200
    assert "Password reset successfully" in response.json()["message"]
    
    # Verify user can login with new password
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "newpassword123"}
    )
    assert login_response.status_code == 200


def test_reset_password_invalid_token(client: TestClient):
    """Test password reset with invalid token"""
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid_token", "password": "newpassword123"}
    )
    assert response.status_code == 400
    assert "Invalid or expired reset token" in response.json()["detail"]