import jwt
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from database import get_db
from models import User, Team, TeamMembership
from security import decode_access_token
from errors import token_expired, forbidden


def get_current_user(
    authorization: str = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise token_expired()
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise token_expired()
    except jwt.InvalidTokenError:
        raise token_expired()

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise token_expired()
    return user


def get_membership(team_id: int, user: User, db: Session) -> TeamMembership | None:
    return (
        db.query(TeamMembership)
        .filter(TeamMembership.team_id == team_id, TeamMembership.user_id == user.id)
        .first()
    )


def require_team_member(team_id: int, user: User, db: Session) -> Team:
    membership = get_membership(team_id, user, db)
    if not membership:
        raise forbidden("이 과제의 멤버가 아닙니다")
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise forbidden("이 과제의 멤버가 아닙니다")
    return team


def require_active_team_member(team_id: int, user: User, db: Session) -> Team:
    team = require_team_member(team_id, user, db)
    if not team.is_active:
        raise forbidden("비활성화된 과제입니다. 쓰기 작업을 할 수 없습니다")
    return team
