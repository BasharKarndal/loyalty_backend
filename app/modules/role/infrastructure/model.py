from uuid import UUID as PyUUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.role_permission.infrastructure.model import RolePermissionModel
from app.modules.user_role.infrastructure.model import UserRoleModel


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    role_permissions: Mapped[list[RolePermissionModel]] = relationship(
    "RolePermissionModel",
    back_populates="role",
    cascade="all, delete-orphan",
)
    user_roles: Mapped[list[UserRoleModel]] = relationship(
    "UserRoleModel",
    back_populates="role",
)