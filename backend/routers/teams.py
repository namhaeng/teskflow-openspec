import random
import string

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Team
from schemas import TeamCreateRequest, TeamJoinRequest, TeamOut, TeamPreviewOut, MemberOut
from security import INVITE_CODE_RE
from dependencies import get_current_user, require_team_member
from errors import validation_error, not_found, already_in_team, forbidden

router = APIRouter(prefix="/teams", tags=["teams"])


def generate_invite_code(db: Session) -> str:
    while True:
        letters = "".join(random.choices(string.ascii_uppercase, k=4))
        digits = "".join(random.choices(string.digits, k=4))
        code = f"{letters}-{digits}"
        if not db.query(Team).filter(Team.invite_code == code).first():
            return code


@router.post("", status_code=201, response_model=TeamOut)
def create_team(
    payload: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (1 <= len(payload.name) <= 30):
        raise validation_error("팀 이름은 1-30자여야 합니다")

    team = Team(name=payload.name, invite_code=generate_invite_code(db), owner_id=current_user.id)
    db.add(team)
    db.flush()

    current_user.team_id = team.id
    db.add(current_user)
    db.commit()
    db.refresh(team)

    return TeamOut(id=team.id, name=team.name, invite_code=team.invite_code, owner_id=team.owner_id)


@router.get("/preview", response_model=TeamPreviewOut)
def preview_team(
    invite_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not INVITE_CODE_RE.match(invite_code or ""):
        raise validation_error("형식이 올바르지 않습니다 (예: FRNT-2026)")

    team = db.query(Team).filter(Team.invite_code == invite_code).first()
    if not team:
        raise not_found("해당 초대코드를 찾을 수 없습니다")

    member_count = db.query(User).filter(User.team_id == team.id).count()
    owner = db.query(User).filter(User.id == team.owner_id).first()
    return TeamPreviewOut(name=team.name, member_count=member_count, owner_email=owner.email if owner else "")


@router.post("/join", response_model=TeamOut)
def join_team(
    payload: TeamJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not INVITE_CODE_RE.match(payload.invite_code or ""):
        raise validation_error("형식이 올바르지 않습니다 (예: FRNT-2026)")

    team = db.query(Team).filter(Team.invite_code == payload.invite_code).first()
    if not team:
        raise not_found("해당 초대코드를 찾을 수 없습니다")

    if current_user.team_id is not None and current_user.team_id != team.id:
        raise already_in_team()

    current_user.team_id = team.id
    db.add(current_user)
    db.commit()

    return TeamOut(id=team.id, name=team.name, invite_code=team.invite_code, owner_id=team.owner_id)


@router.delete("/{team_id}/leave")
def leave_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_team_member(team_id, current_user, db)
    current_user.team_id = None
    db.add(current_user)
    db.commit()
    return {}


@router.get("/{team_id}", response_model=TeamOut)
def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = require_team_member(team_id, current_user, db)
    return TeamOut(id=team.id, name=team.name, invite_code=team.invite_code, owner_id=team.owner_id)


@router.get("/{team_id}/members", response_model=list[MemberOut])
def list_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = require_team_member(team_id, current_user, db)
    members = db.query(User).filter(User.team_id == team_id).all()
    return [
        MemberOut(
            id=m.id,
            email=m.email,
            role="owner" if m.id == team.owner_id else "member",
            created_at=m.created_at.isoformat(),
        )
        for m in members
    ]
