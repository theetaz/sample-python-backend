from pydantic import BaseModel
from typing import Optional
import uuid as uuid_pkg


class CreateComplaint(BaseModel):
    description: str
    category: str
    place: str
    images: Optional[str]
    user_id: uuid_pkg.UUID


class UpdateComplaint(BaseModel):
    description: Optional[str]
    category: Optional[str]
    place: Optional[str]
    images: Optional[str]


class CreateUser(BaseModel):
    name: str
    email: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


class LoginUser(BaseModel):
    email: str
    password: str


class SsoUserLoginRequest(BaseModel):
    email: str
    name: str
    image: Optional[str]
    provider: Optional[str]
    provider_id: Optional[str]


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str


class PasswordResetRequestRequest(BaseModel):
    email: str


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[str]
    hashed_password: Optional[str]
    wallet_address: Optional[str]
    profile_image: Optional[str]
    role: Optional[str]
    is_admin: Optional[bool]
    is_active: Optional[bool]


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
