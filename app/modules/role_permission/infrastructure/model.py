from typing import TYPE_CHECKING
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.role.infrastructure.model import RoleModel
    from app.modules.Permission.infrastructure.model import PermissionModel


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission",
        ),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    role_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
    )

    permission_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id"),
        nullable=False,
    )

    role: Mapped["RoleModel"] = relationship(
        "RoleModel",
        back_populates="role_permissions",
    )

    permission: Mapped["PermissionModel"] = relationship(
        "PermissionModel",
        back_populates="role_permissions",
    )