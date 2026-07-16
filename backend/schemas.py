from typing import Optional
from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    team_id: Optional[int] = None


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class TeamCreateRequest(BaseModel):
    name: str


class TeamJoinRequest(BaseModel):
    invite_code: str


class TeamOut(BaseModel):
    id: int
    name: str
    invite_code: str
    owner_id: int


class TeamPreviewOut(BaseModel):
    name: str
    member_count: int
    owner_email: str


class MemberOut(BaseModel):
    id: int
    email: str
    role: str
    created_at: str


class TaskCreateRequest(BaseModel):
    title: str
    assignee_id: Optional[int] = None


class TaskTitleUpdateRequest(BaseModel):
    title: str
    assignee_id: Optional[int] = None


class TaskStatusUpdateRequest(BaseModel):
    status: str


class TaskOut(BaseModel):
    id: int
    team_id: int
    title: str
    status: str
    creator_id: int
    assignee_id: Optional[int] = None
    created_at: str


class MessageCreateRequest(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    team_id: int
    user_id: int
    user_email: str
    content: str
    created_at: str
