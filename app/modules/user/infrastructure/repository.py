from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.role.infrastructure.model import RoleModel
from app.modules.role_permission.infrastructure.model import RolePermissionModel
from app.modules.user.application.dto.user_permissions_dto import (
    PermissionDto,
    RolePermissionsDto,
    UserPermissionsDto,
)
from app.modules.user.domain.entity import User
from app.modules.user.domain.repository import UserRepository
from app.modules.user_role.infrastructure.model import UserRoleModel

from .mapper import UserMapper
from .model import UserModel


class SqlAlchemyUserRepository(UserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> None:
        model = UserMapper.to_model(user)
        self.session.add(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        if user_model is None:
            return None
        return UserMapper.to_domain(user_model)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return UserMapper.to_domain(model)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return UserMapper.to_domain(model)

    async def list(self) -> list[User]:
        result = await self.session.execute(select(UserModel))
        models = result.scalars().all()
        return [UserMapper.to_domain(model) for model in models]

    async def update(self, user: User) -> None:
        model = await self.session.get(UserModel, user.id)
        if model is None:
            return

        model.full_name = user.full_name
        model.email = user.email
        model.phone = user.phone
        model.national_id = user.national_id
        model.is_active = user.is_active
        model.password_hash = user.password_hash

    async def get_permissions(self, user_id: UUID) -> UserPermissionsDto | None:
        stmt = (
            select(UserModel)
            .options(
                joinedload(UserModel.user_roles)
                .joinedload(UserRoleModel.role)
                .joinedload(RoleModel.role_permissions)
                .joinedload(RolePermissionModel.permission)
            )
            .where(UserModel.id == user_id)
        )

        result = await self.session.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if user is None:
            return None

        roles = []
        for user_role in user.user_roles:
            role = user_role.role
            if not role.is_active:
                continue

            permissions = []
            for role_permission in role.role_permissions:
                permission = role_permission.permission
                if not permission.is_active:
                    continue

                permissions.append(
                    PermissionDto(
                        id=permission.id,
                        name=permission.name,
                    )
                )

            roles.append(
                RolePermissionsDto(
                    id=role.id,
                    name=role.name,
                    permissions=permissions,
                )
            )

        return UserPermissionsDto(
            user_id=user.id,
            username=user.username,
            roles=roles,
        )

    async def get_by_id_no_ditels(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return UserMapper.to_domain(model)
