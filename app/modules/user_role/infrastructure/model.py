from typing import TYPE_CHECKING
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.modules.user.infrastructure.model import UserModel
    from app.modules.role.infrastructure.model import RoleModel


class UserRoleModel(Base):

    __tablename__ = "user_roles"


    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )


    role_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
    )


    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="user_roles",
    )


    role: Mapped["RoleModel"] = relationship(
        "RoleModel",
        back_populates="user_roles",
    )