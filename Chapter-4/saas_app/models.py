from enum import Enum
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

class Base(DeclarativeBase):
    pass

class Role(str, Enum):
    basic = "basic"
    premium = "premium"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    username: Mapped[str] = mapped_column(
        unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        unique=True, index=True
    )
    role: Mapped[Role] = mapped_column(
        default=Role.basic
    )
    hashed_password: Mapped[str]
    totp_secret: Mapped[str] = mapped_column(
        nullable=True
)
   