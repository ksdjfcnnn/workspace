from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.employee import Employee
from app.models.organization import Organization
from app.core.security import get_password_hash
import uuid
from datetime import datetime

def create_test_users():
    db = SessionLocal()
    try:
        # Create organization if it doesn't exist
        org = db.query(Organization).first()
        if not org:
            org = Organization(
                id=str(uuid.uuid4()).replace('-', ''),
                name="Test Organization",
                domain="example.com",
                createdAt=int(datetime.utcnow().timestamp() * 1000)
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"Created organization: {org.name} with ID: {org.id}")
        
        # Create admin user
        admin = db.query(Employee).filter(Employee.email == "admin@example.com").first()
        if not admin:
            admin = Employee(
                name="Admin User",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                organizationId=org.id,
                isAdmin=True,
                emailVerified=True,
                createdAt=int(datetime.utcnow().timestamp() * 1000)
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Created admin user: {admin.email} with ID: {admin.id}")
        
        # Create regular user
        user = db.query(Employee).filter(Employee.email == "user@example.com").first()
        if not user:
            user = Employee(
                name="Regular User",
                email="user@example.com",
                password_hash=get_password_hash("user123"),
                organizationId=org.id,
                isAdmin=False,
                emailVerified=True,
                createdAt=int(datetime.utcnow().timestamp() * 1000)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created regular user: {user.email} with ID: {user.id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    create_test_users()