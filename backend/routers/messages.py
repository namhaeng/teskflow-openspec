from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Message
from schemas import MessageCreateRequest, MessageOut
from dependencies import get_current_user, require_team_member
from errors import too_long, not_found, not_owner

router = APIRouter(tags=["messages"])

MAX_MESSAGE_LENGTH = 1000


def _to_out(message: Message, email: str) -> MessageOut:
    return MessageOut(
        id=message.id,
        team_id=message.team_id,
        user_id=message.user_id,
        user_email=email,
        content=message.content,
        created_at=message.created_at.isoformat(),
    )


@router.get("/teams/{team_id}/messages", response_model=list[MessageOut])
def list_messages(
    team_id: int,
    since: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_team_member(team_id, current_user, db)
    query = db.query(Message).filter(Message.team_id == team_id)
    if since:
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        query = query.filter(Message.created_at > since_dt)
    else:
        query = query.order_by(Message.created_at.desc()).limit(50)
        messages = list(reversed(query.all()))
        return _with_emails(messages, db)

    messages = query.order_by(Message.created_at.asc()).all()
    return _with_emails(messages, db)


def _with_emails(messages: list[Message], db: Session) -> list[MessageOut]:
    user_ids = {m.user_id for m in messages}
    users = {u.id: u.email for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    return [_to_out(m, users.get(m.user_id, "")) for m in messages]


@router.post("/teams/{team_id}/messages", status_code=201, response_model=MessageOut)
def create_message(
    team_id: int,
    payload: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_team_member(team_id, current_user, db)
    if len(payload.content) > MAX_MESSAGE_LENGTH:
        raise too_long(MAX_MESSAGE_LENGTH, len(payload.content))

    message = Message(team_id=team_id, user_id=current_user.id, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return _to_out(message, current_user.email)


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise not_found()
    require_team_member(message.team_id, current_user, db)
    if message.user_id != current_user.id:
        raise not_owner()
    db.delete(message)
    db.commit()
    return {}
