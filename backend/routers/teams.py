import random
import string

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Team, TeamMembership
from schemas import (
    TeamCreateRequest,
    TeamJoinRequest,
    TeamOut,
    TeamPreviewOut,
    TeamActiveUpdateRequest,
    MemberOut,
)
from security import INVITE_CODE_RE
from dependencies import get_current_user, require_team_member, get_membership
from errors import validation_error, not_found, already_in_team, forbidden

router = APIRouter(prefix="/teams", tags=["teams"])


def generate_invite_code(db: Session) -> str:
    while True:
        letters = "".join(random.choices(string.ascii_uppercase, k=4))
        digits = "".join(random.choices(string.digits, k=4))
        code = f"{letters}-{digits}"
        if not db.query(Team).filter(Team.invite_code == code).first():
            return code


def _to_out(team: Team, role: str | None = None) -> TeamOut:
    return TeamOut(
        id=team.id,
        name=team.name,
        invite_code=team.invite_code,
        owner_id=team.owner_id,
        is_active=team.is_active,
        role=role,
    )


@router.post("", status_code=201, response_model=TeamOut)
def create_team(
    payload: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (1 <= len(payload.name) <= 30):
        raise validation_error("과제 이름은 1-30자여야 합니다")

    team = Team(name=payload.name, invite_code=generate_invite_code(db), owner_id=current_user.id)
    db.add(team)
    db.flush()

    db.add(TeamMembership(team_id=team.id, user_id=current_user.id, role="owner"))
    db.commit()
    db.refresh(team)

    return _to_out(team, role="owner")


@router.get("/mine", response_model=list[TeamOut])
def list_my_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Team, TeamMembership.role)
        .join(TeamMembership, TeamMembership.team_id == Team.id)
        .filter(TeamMembership.user_id == current_user.id)
        .order_by(Team.created_at.asc())
        .all()
    )
    return [_to_out(team, role=role) for team, role in rows]


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

    member_count = db.query(TeamMembership).filter(TeamMembership.team_id == team.id).count()
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

    if get_membership(team.id, current_user, db):
        raise already_in_team()

    db.add(TeamMembership(team_id=team.id, user_id=current_user.id, role="member"))
    db.commit()

    return _to_out(team, role="member")


@router.delete("/{team_id}/leave")
def leave_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = get_membership(team_id, current_user, db)
    if not membership:
        raise forbidden("이 과제의 멤버가 아닙니다")
    if membership.role == "owner":
        raise forbidden("owner는 과제를 나갈 수 없습니다. 대신 비활성화하세요")
    db.delete(membership)
    db.commit()
    return {}


@router.patch("/{team_id}/active", response_model=TeamOut)
def update_team_active(
    team_id: int,
    payload: TeamActiveUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = require_team_member(team_id, current_user, db)
    if team.owner_id != current_user.id:
        raise forbidden("owner만 과제 활성 상태를 변경할 수 있습니다")
    team.is_active = payload.is_active
    db.add(team)
    db.commit()
    db.refresh(team)
    membership = get_membership(team_id, current_user, db)
    return _to_out(team, role=membership.role if membership else None)


@router.get("/{team_id}", response_model=TeamOut)
def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = require_team_member(team_id, current_user, db)
    membership = get_membership(team_id, current_user, db)
    return _to_out(team, role=membership.role if membership else None)


@router.get("/{team_id}/members", response_model=list[MemberOut])
def list_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_team_member(team_id, current_user, db)
    rows = (
        db.query(User, TeamMembership.role, TeamMembership.created_at)
        .join(TeamMembership, TeamMembership.user_id == User.id)
        .filter(TeamMembership.team_id == team_id)
        .all()
    )
    return [
        MemberOut(id=u.id, email=u.email, role=role, created_at=joined_at.isoformat())
        for u, role, joined_at in rows
    ]
