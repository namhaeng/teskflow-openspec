from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Task
from schemas import TaskCreateRequest, TaskTitleUpdateRequest, TaskStatusUpdateRequest, TaskOut
from dependencies import get_current_user, require_team_member, require_active_team_member
from errors import validation_error, not_found, forbidden

router = APIRouter(tags=["tasks"])

VALID_STATUSES = {"TODO", "DOING", "DONE"}


def _to_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        team_id=task.team_id,
        title=task.title,
        status=task.status,
        creator_id=task.creator_id,
        assignee_id=task.assignee_id,
        created_at=task.created_at.isoformat(),
    )


@router.get("/teams/{team_id}/tasks", response_model=list[TaskOut])
def list_tasks(
    team_id: int,
    filter: str = Query(default="all", pattern="^(all|me|unassigned)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_team_member(team_id, current_user, db)
    query = db.query(Task).filter(Task.team_id == team_id)
    if filter == "me":
        query = query.filter(Task.assignee_id == current_user.id)
    elif filter == "unassigned":
        query = query.filter(Task.assignee_id.is_(None))
    tasks = query.order_by(Task.created_at.desc()).all()
    return [_to_out(t) for t in tasks]


@router.post("/teams/{team_id}/tasks", status_code=201, response_model=TaskOut)
def create_task(
    team_id: int,
    payload: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_active_team_member(team_id, current_user, db)
    if not (1 <= len(payload.title) <= 100):
        raise validation_error("제목은 1-100자여야 합니다")

    task = Task(
        team_id=team_id,
        title=payload.title,
        status="TODO",
        creator_id=current_user.id,
        assignee_id=payload.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_out(task)


def _get_task_in_team(task_id: int, current_user: User, db: Session, active_required: bool = False) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise not_found()
    if active_required:
        require_active_team_member(task.team_id, current_user, db)
    else:
        require_team_member(task.team_id, current_user, db)
    return task


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _get_task_in_team(task_id, current_user, db)
    return _to_out(task)


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task_title(
    task_id: int,
    payload: TaskTitleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = _get_task_in_team(task_id, current_user, db, active_required=True)
    if not (1 <= len(payload.title) <= 100):
        raise validation_error("제목은 1-100자여야 합니다")
    task.title = payload.title
    task.assignee_id = payload.assignee_id
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_out(task)


@router.patch("/tasks/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = _get_task_in_team(task_id, current_user, db, active_required=True)
    if payload.status not in VALID_STATUSES:
        raise validation_error("status는 TODO, DOING, DONE 중 하나여야 합니다")
    task.status = payload.status
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_out(task)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _get_task_in_team(task_id, current_user, db, active_required=True)
    team = require_active_team_member(task.team_id, current_user, db)
    if current_user.id != task.creator_id and current_user.id != team.owner_id:
        raise forbidden()
    db.delete(task)
    db.commit()
    return {}
