from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import SignupRequest, LoginRequest, AuthResponse, UserOut
from security import is_valid_email, hash_password, verify_password, create_access_token
from dependencies import get_current_user
from errors import validation_error, email_taken, invalid_credentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201, response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if not is_valid_email(payload.email):
        raise validation_error("올바른 이메일 형식이 아닙니다")
    if len(payload.password) < 8:
        raise validation_error("8자 이상 입력해주세요")
    if db.query(User).filter(User.email == payload.email).first():
        raise email_taken()

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return AuthResponse(token=token, user=UserOut(id=user.id, email=user.email, team_id=user.team_id))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials()

    token = create_access_token(user.id)
    return AuthResponse(token=token, user=UserOut(id=user.id, email=user.email, team_id=user.team_id))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # stateless: no server-side blacklist, client discards the token
    return {}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, email=current_user.email, team_id=current_user.team_id)
