import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.database import Base, get_db
from app.main import app
from app.models import *
from app.core.security import create_access_token, get_password_hash
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create tables for each test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_organization(db):
    from app.models.organization import Organization
    org = Organization(
        name="Test Organization",
        domain="test.com"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_team(db, test_organization):
    from app.models.team import Team
    team = Team(
        name="Test Team",
        organizationId=test_organization.id
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@pytest.fixture
def test_admin_user(db, test_organization, test_team):
    from app.models.employee import Employee
    admin = Employee(
        name="Admin User",
        email="admin@test.com",
        password_hash=get_password_hash("password123"),
        organizationId=test_organization.id,
        teamId=test_team.id,
        isAdmin=True,
        emailVerified=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def test_user(db, test_organization, test_team):
    from app.models.employee import Employee
    user = Employee(
        name="Test User",
        email="user@test.com",
        password_hash=get_password_hash("password123"),
        organizationId=test_organization.id,
        teamId=test_team.id,
        isAdmin=False,
        emailVerified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(test_admin_user):
    return create_access_token(
        data={"sub": test_admin_user.id, "email": test_admin_user.email, "isAdmin": True}
    )


@pytest.fixture
def user_token(test_user):
    return create_access_token(
        data={"sub": test_user.id, "email": test_user.email, "isAdmin": False}
    )


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def test_project(db, test_organization, test_admin_user):
    from app.models.project import Project
    project = Project(
        name="Test Project",
        description="A test project",
        organizationId=test_organization.id,
        creatorId=test_admin_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def test_task(db, test_organization, test_project, test_admin_user):
    from app.models.task import Task
    task = Task(
        name="Test Task",
        description="A test task",
        projectId=test_project.id,
        organizationId=test_organization.id,
        creatorId=test_admin_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task