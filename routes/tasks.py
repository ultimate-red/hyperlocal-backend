from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User, Task, TaskStatus
from schemas import TaskCreate, TaskResponse
from auth import verify_token

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_current_user_id(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> int:
    """
    Extract user ID from JWT token
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        user_id = int(payload.get("sub"))
        return user_id
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new task
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        reward=task_data.reward,
        created_by=user_id,
        status=TaskStatus.OPEN
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Add creator name to response
    creator = db.query(User).filter(User.id == task.created_by).first()
    task_response = TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        reward=task.reward,
        status=task.status.value,
        created_by=task.created_by,
        accepted_by=task.accepted_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
        creator_name=creator.name if creator else None,
        acceptor_name=None
    )
    
    return task_response

@router.get("/", response_model=List[TaskResponse])
def get_all_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all tasks (no filtering in Phase 0)
    """
    tasks = db.query(Task).filter(Task.status == TaskStatus.OPEN).order_by(Task.created_at.desc()).all()
    
    task_responses = []
    for task in tasks:
        creator = db.query(User).filter(User.id == task.created_by).first()
        acceptor = db.query(User).filter(User.id == task.accepted_by).first() if task.accepted_by else None
        
        task_responses.append(TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            reward=task.reward,
            status=task.status.value,
            created_by=task.created_by,
            accepted_by=task.accepted_by,
            created_at=task.created_at,
            updated_at=task.updated_at,
            creator_name=creator.name if creator else creator.phone if creator else None,
            acceptor_name=acceptor.name if acceptor else acceptor.phone if acceptor else None
        ))
    
    return task_responses

@router.get("/mine/posted", response_model=List[TaskResponse])
def get_my_posted_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    tasks = db.query(Task).filter(
        Task.created_by == user_id
    ).order_by(Task.created_at.desc()).all()

    result = []
    for task in tasks:
        creator  = db.query(User).filter(User.id == task.created_by).first()
        acceptor = db.query(User).filter(User.id == task.accepted_by).first() if task.accepted_by else None
        result.append(TaskResponse(
            id=task.id, title=task.title, description=task.description,
            reward=task.reward, status=task.status.value,
            created_by=task.created_by, accepted_by=task.accepted_by,
            created_at=task.created_at, updated_at=task.updated_at,
            creator_name=creator.name if creator else None,
            acceptor_name=acceptor.name if acceptor else None,
        ))
    return result


@router.get("/mine/taken", response_model=List[TaskResponse])
def get_my_taken_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    tasks = db.query(Task).filter(
        Task.accepted_by == user_id
    ).order_by(Task.created_at.desc()).all()

    result = []
    for task in tasks:
        creator  = db.query(User).filter(User.id == task.created_by).first()
        acceptor = db.query(User).filter(User.id == task.accepted_by).first() if task.accepted_by else None
        result.append(TaskResponse(
            id=task.id, title=task.title, description=task.description,
            reward=task.reward, status=task.status.value,
            created_by=task.created_by, accepted_by=task.accepted_by,
            created_at=task.created_at, updated_at=task.updated_at,
            creator_name=creator.name if creator else None,
            acceptor_name=acceptor.name if acceptor else None,
        ))
    return result


@router.get("/mine", response_model=List[TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    tasks = db.query(Task).filter(
        or_(Task.created_by == user_id, Task.accepted_by == user_id)
    ).order_by(Task.created_at.desc()).all()

    result = []
    for task in tasks:
        creator  = db.query(User).filter(User.id == task.created_by).first()
        acceptor = db.query(User).filter(User.id == task.accepted_by).first() if task.accepted_by else None
        result.append(TaskResponse(
            id=task.id, title=task.title, description=task.description,
            reward=task.reward, status=task.status.value,
            created_by=task.created_by, accepted_by=task.accepted_by,
            created_at=task.created_at, updated_at=task.updated_at,
            creator_name=creator.name if creator else None,
            acceptor_name=acceptor.name if acceptor else None,
        ))
    return result


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get a specific task by ID
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    creator = db.query(User).filter(User.id == task.created_by).first()
    acceptor = db.query(User).filter(User.id == task.accepted_by).first() if task.accepted_by else None
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        reward=task.reward,
        status=task.status.value,
        created_by=task.created_by,
        accepted_by=task.accepted_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
        creator_name=creator.name if creator else creator.phone if creator else None,
        acceptor_name=acceptor.name if acceptor else acceptor.phone if acceptor else None
    )

@router.post("/{task_id}/accept", response_model=TaskResponse)
def accept_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Accept a task
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status != TaskStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not available"
        )
    
    if task.created_by == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot accept your own task"
        )
    
    task.accepted_by = user_id
    task.status = TaskStatus.ACCEPTED
    db.commit()
    db.refresh(task)
    
    creator = db.query(User).filter(User.id == task.created_by).first()
    acceptor = db.query(User).filter(User.id == task.accepted_by).first()
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        reward=task.reward,
        status=task.status.value,
        created_by=task.created_by,
        accepted_by=task.accepted_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
        creator_name=creator.name if creator else creator.phone if creator else None,
        acceptor_name=acceptor.name if acceptor else acceptor.phone if acceptor else None
    )

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark task as completed
    Only the task creator can mark it as completed
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task creator can mark task as completed"
        )
    
    if task.status != TaskStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task must be accepted before completing"
        )
    
    task.status = TaskStatus.COMPLETED
    db.commit()
    db.refresh(task)
    
    creator = db.query(User).filter(User.id == task.created_by).first()
    acceptor = db.query(User).filter(User.id == task.accepted_by).first()
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        reward=task.reward,
        status=task.status.value,
        created_by=task.created_by,
        accepted_by=task.accepted_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
        creator_name=creator.name if creator else creator.phone if creator else None,
        acceptor_name=acceptor.name if acceptor else acceptor.phone if acceptor else None
    )
