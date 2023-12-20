import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import text
from sqlmodel import Field, SQLModel


class UUIDModel(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text(
            "gen_random_uuid()"), "unique": True},
    )


class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )


class User(UUIDModel, TimestampModel, table=True):
    __tablename__ = "users"

    name: str = Field(nullable=False)
    email: str = Field(nullable=False, index=True, unique=True)
    hashed_password: str = Field(nullable=False)
    wallet_address: str = Field(nullable=True)
    profile_image: str = Field(nullable=True)
    role = Field(nullable=False, default="user", index=True)
    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=False)

    def dict(self, **kwargs):
        user_dict = super().dict(**kwargs)
        user_dict.pop("hashed_password", None)
        return user_dict


class Complaint(UUIDModel, TimestampModel, table=True):
    __tablename__ = "complaints"

    description: str = Field(nullable=False)
    category: str = Field(nullable=False)
    place: str = Field(nullable=True)
    images: str = Field(nullable=True)
    user_id: uuid_pkg.UUID = Field(nullable=False)
    status: str = Field(nullable=False, default="pending")
    note: str = Field(nullable=True)


metadata = SQLModel.metadata
