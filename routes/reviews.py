from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user_id
from database import get_db
from models import Review, Task, User
from schemas import ReviewCreate, ReviewResponse

router = APIRouter(tags=["Reviews"])


def _to_response(review: Review, db: Session) -> ReviewResponse:
    reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
    return ReviewResponse(
        id=review.id,
        task_id=review.task_id,
        reviewer_id=review.reviewer_id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment,
        reviewer_name=reviewer.name if reviewer else None,
        created_at=review.created_at,
    )


@router.post("/tasks/{task_id}/review", response_model=ReviewResponse, status_code=201)
def submit_review(
    task_id: int,
    data: ReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    is_creator  = task.created_by  == user_id
    is_acceptor = task.accepted_by == user_id

    if not is_creator and not is_acceptor:
        raise HTTPException(status_code=403, detail="Not involved in this task")

    if is_creator:
        if task.status not in ("completed", "aborted"):
            raise HTTPException(status_code=400, detail="Can only review after task is completed or aborted")
        if not task.accepted_by:
            raise HTTPException(status_code=400, detail="No acceptor to review")
        reviewee_id = task.accepted_by
    else:
        if task.status not in ("completed", "aborted") and not task.hidden_from_creator:
            raise HTTPException(status_code=400, detail="Can only review after task ends or is removed by creator")
        reviewee_id = task.created_by

    existing = db.query(Review).filter(
        Review.task_id == task_id,
        Review.reviewer_id == user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this task")

    review = Review(
        task_id=task_id,
        reviewer_id=user_id,
        reviewee_id=reviewee_id,
        rating=data.rating,
        comment=data.comment.strip() if data.comment else None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _to_response(review, db)


@router.get("/tasks/{task_id}/my-review", response_model=Optional[ReviewResponse])
def get_my_review(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(
        Review.task_id == task_id,
        Review.reviewer_id == user_id,
    ).first()
    if not review:
        return None
    return _to_response(review, db)
