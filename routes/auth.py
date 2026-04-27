from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import User
from schemas import UserCreate, OTPVerify, Token, UserResponse
from auth import generate_otp, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request-otp")
def request_otp(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Request OTP for login/signup.
    In Phase 0, we just generate and store OTP (no SMS sending).
    In production, integrate with SMS service.
    """
    user = db.query(User).filter(User.phone == user_data.phone).first()
    
    otp = generate_otp()
    otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    
    if user:
        # Update existing user
        user.otp = otp
        user.otp_expiry = otp_expiry
    else:
        # Create new user
        user = User(
            phone=user_data.phone,
            otp=otp,
            otp_expiry=otp_expiry
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # In Phase 0, return OTP in response (ONLY FOR TESTING!)
    # Remove this in production and send via SMS
    return {
        "message": "OTP sent successfully",
        "phone": user_data.phone,
        "otp": otp  # REMOVE IN PRODUCTION
    }

@router.post("/verify-otp", response_model=Token)
def verify_otp(verify_data: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify OTP and return access token
    """
    user = db.query(User).filter(User.phone == verify_data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check OTP
    if user.otp != verify_data.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP"
        )
    
    # Check OTP expiry
    if user.otp_expiry < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP expired"
        )
    
    # Mark user as verified
    user.is_verified = 1
    user.otp = None
    user.otp_expiry = None
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "phone": user.phone})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(lambda: None)  # Simplified for Phase 0
):
    """
    Get current user details
    """
    # This is simplified for Phase 0
    # In production, properly decode token from Authorization header
    pass
