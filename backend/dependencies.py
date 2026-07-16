import jwt
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from database import get_db
from models import User, Team
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


def require_team_member(team_id: int, user: User, db: Session) -> Team:
    if user.team_id != team_id:
        raise forbidden("이 팀의 멤버가 아닙니다")
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise forbidden("이 팀의 멤버가 아닙니다")
    return team
