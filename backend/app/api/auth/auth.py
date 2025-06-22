from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import Token, LoginRequest, EmailVerificationRequest, PasswordResetRequest
from app.services.employee_service import EmployeeService
from app.services.email_service import email_service
from app.core.security import (
    verify_password, 
    create_access_token, 
    verify_email_verification_token,
    create_email_verification_token
)
from datetime import timedelta
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login endpoint for both admin and regular users"""
    employee_service = EmployeeService(db)
    user = employee_service.get_employee_by_email(login_data.email)
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.emailVerified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your email for verification link."
        )
    
    if user.deactivated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "isAdmin": user.isAdmin},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify email and set password for new employees"""
    try:
        email = verify_email_verification_token(verification_data.token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    employee_service = EmployeeService(db)
    user = employee_service.verify_email_and_set_password(email, verification_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Email verified and password set successfully"}


@router.post("/forgot-password")
async def forgot_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    employee_service = EmployeeService(db)
    user = employee_service.get_employee_by_email(reset_data.email)
    
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    if not user.emailVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified. Please contact your administrator."
        )
    
    # Send password reset email
    email_sent = email_service.send_password_reset(user.email, user.name)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: EmailVerificationRequest,  # Reusing the same schema
    db: Session = Depends(get_db)
):
    """Reset password using token"""
    try:
        email = verify_email_verification_token(reset_data.token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    employee_service = EmployeeService(db)
    user = employee_service.get_employee_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    from app.core.security import get_password_hash
    user.password_hash = get_password_hash(reset_data.password)
    db.commit()
    
    return {"message": "Password reset successfully"}