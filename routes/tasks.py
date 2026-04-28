from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, Task, TaskStatus
from schemas import TaskAbort, TaskCreate, TaskResponse
from auth import verify_token

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ── Auth dependency ────────────────────────────────────────────────────────────

def get_current_user_id(authorization: Optional[str] = Header(None),
                        db: Session = Depends(get_db)) -> int:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token")
        return int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")


# ── Helper ─────────────────────────────────────────────────────────────────────

def _resp(task: Task, db: Session) -> TaskResponse:
    creator  = db.query(User).filter(User.id == task.created_by).first()
    acceptor = db.query(User).filter(User.id == task.accepted_by).first() if task.accepted_by else None
    return TaskResponse(
        id=task.id, title=task.title, description=task.description,
        reward=task.reward, status=task.status,
        created_by=task.created_by, accepted_by=task.accepted_by,
        abort_reason=task.abort_reason,
        hidden_from_creator=task.hidden_from_creator,
        hidden_from_acceptor=task.hidden_from_acceptor,
        created_at=task.created_at, updated_at=task.updated_at,
        creator_name=creator.name if creator else None,
        acceptor_name=acceptor.name if acceptor else None,
    )


def _get_or_404(task_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


# ── Public feed ────────────────────────────────────────────────────────────────

@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    task = Task(
        title=task_data.title, description=task_data.description,
        reward=task_data.reward, created_by=user_id,
        status=TaskStatus.OPEN.value,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _resp(task, db)


@router.get("/", response_model=List[TaskResponse])
def get_open_tasks(db: Session = Depends(get_db),
                   user_id: int = Depends(get_current_user_id)):
    tasks = (db.query(Task)
               .filter(Task.status == TaskStatus.OPEN,
                       Task.hidden_from_creator == False,
                       Task.created_by != user_id)
               .order_by(Task.created_at.desc()).all())
    return [_resp(t, db) for t in tasks]


# ── My tasks ───────────────────────────────────────────────────────────────────

@router.get("/mine/posted", response_model=List[TaskResponse])
def get_my_posted(db: Session = Depends(get_db),
                  user_id: int = Depends(get_current_user_id)):
    tasks = (db.query(Task)
               .filter(Task.created_by == user_id,
                       Task.hidden_from_creator == False)
               .order_by(Task.created_at.desc()).all())
    return [_resp(t, db) for t in tasks]


@router.get("/mine/taken", response_model=List[TaskResponse])
def get_my_taken(db: Session = Depends(get_db),
                 user_id: int = Depends(get_current_user_id)):
    tasks = (db.query(Task)
               .filter(Task.accepted_by == user_id,
                       Task.hidden_from_acceptor == False)
               .order_by(Task.created_at.desc()).all())
    return [_resp(t, db) for t in tasks]


@router.get("/mine", response_model=List[TaskResponse])
def get_mine(db: Session = Depends(get_db),
             user_id: int = Depends(get_current_user_id)):
    tasks = (db.query(Task)
               .filter(or_(Task.created_by == user_id, Task.accepted_by == user_id))
               .order_by(Task.created_at.desc()).all())
    return [_resp(t, db) for t in tasks]


# ── Single task ────────────────────────────────────────────────────────────────

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db),
             user_id: int = Depends(get_current_user_id)):
    return _resp(_get_or_404(task_id, db), db)


# ── Actions ────────────────────────────────────────────────────────────────────

@router.post("/{task_id}/accept", response_model=TaskResponse)
def accept_task(task_id: int, db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    task = _get_or_404(task_id, db)
    if task.status != TaskStatus.OPEN:
        raise HTTPException(status_code=400, detail="Task is not available")
    if task.created_by == user_id:
        raise HTTPException(status_code=400, detail="Cannot accept your own task")
    task.accepted_by = user_id
    task.status = TaskStatus.ACCEPTED.value
    db.commit()
    db.refresh(task)
    return _resp(task, db)


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db),
                  user_id: int = Depends(get_current_user_id)):
    task = _get_or_404(task_id, db)
    if task.status != TaskStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Task must be accepted before completing")
    if task.accepted_by != user_id:
        raise HTTPException(status_code=403, detail="Only the acceptor can mark this task complete")
    task.status = TaskStatus.COMPLETED.value
    db.commit()
    db.refresh(task)
    return _resp(task, db)


@router.post("/{task_id}/abort", response_model=TaskResponse)
def abort_task(task_id: int, body: TaskAbort, db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id)):
    task = _get_or_404(task_id, db)
    if task.status != TaskStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Only an accepted task can be aborted")
    if task.accepted_by != user_id:
        raise HTTPException(status_code=403, detail="Only the acceptor can abort this task")
    if not body.reason.strip():
        raise HTTPException(status_code=400, detail="Abort reason is required")
    task.status = TaskStatus.ABORTED.value
    task.abort_reason = body.reason.strip()
    db.commit()
    db.refresh(task)
    return _resp(task, db)


@router.post("/{task_id}/repost", response_model=TaskResponse)
def repost_task(task_id: int, db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    original = _get_or_404(task_id, db)
    if original.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the creator can repost this task")
    if original.status not in (TaskStatus.ABORTED, TaskStatus.COMPLETED):
        raise HTTPException(status_code=400, detail="Only aborted or completed tasks can be reposted")
    new_task = Task(
        title=original.title, description=original.description,
        reward=original.reward, created_by=user_id,
        status=TaskStatus.OPEN.value,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return _resp(new_task, db)


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    task = _get_or_404(task_id, db)
    if task.created_by == user_id:
        task.hidden_from_creator = True
    elif task.accepted_by == user_id:
        task.hidden_from_acceptor = True
    else:
        raise HTTPException(status_code=403, detail="Not authorised to remove this task")
    db.commit()
    return {"message": "Task removed"}
