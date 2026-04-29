from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user_id
from database import get_db
from models import Review, User
from schemas import FCMTokenUpdate, UserProfileUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(user_id: int = Depends(get_current_user_id),
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()
    avg = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
    return {
        "id": user.id, "email": user.email, "name": user.name,
        "profile_picture": user.profile_picture, "bio": user.bio,
        "location": user.location, "phone": user.phone,
        "is_active": user.is_active, "created_at": user.created_at,
        "average_rating": avg, "review_count": len(reviews),
    }


@router.put("/me", response_model=UserResponse)
def update_profile(data: UserProfileUpdate,
                   user_id: int = Depends(get_current_user_id),
                   db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.name     is not None: user.name     = data.name
    if data.bio      is not None: user.bio      = data.bio
    if data.location is not None: user.location = data.location
    if data.phone    is not None: user.phone    = data.phone

    db.commit()
    db.refresh(user)
    return user


@router.put("/me/fcm-token")
def update_fcm_token(data: FCMTokenUpdate,
                     user_id: int = Depends(get_current_user_id),
                     db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.fcm_token = data.token
    db.commit()
    return {"message": "FCM token updated"}
