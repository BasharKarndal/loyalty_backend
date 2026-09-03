from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import AppException
from app.core.security.jwt import decode_access_token
from app.modules.user.domain.entity import User
from app.modules.user.infrastructure.unit_of_work import SqlAlchemyUserUnitOfWork
from app.shared.access import assert_workspace_access, is_super_admin
from app.shared.tenancy import (
    set_current_owner_id,
    set_unrestricted_view,
    set_workspace_owner_id,
)

security = HTTPBearer(auto_error=False)


async def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise AppException(
            message="Authentication token is required.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=["UNAUTHORIZED"],
        )

    try:
        return decode_access_token(credentials.credentials)
    except Exception as exc:
        raise AppException(
            message="Authentication token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=["INVALID_TOKEN"],
        ) from exc


async def get_current_user(
    request: Request,
    token: dict = Depends(get_current_token),
    session: AsyncSession = Depends(get_session),
) -> User:
    uow = SqlAlchemyUserUnitOfWork(session)
    user = await uow.users.get_by_id(UUID(token["sub"]))

    if user is None:
        raise AppException(
            message="User not found.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=["USER_NOT_FOUND"],
        )

    if not user.is_active:
        raise AppException(
            message="User is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=["USER_INACTIVE"],
        )

    await assert_workspace_access(session, user)
    set_current_owner_id(user.id)

    if await is_super_admin(session, user.id):
        set_unrestricted_view(True)
        raw_workspace = request.headers.get("x-workspace-owner-id")
        workspace_id = None
        if raw_workspace:
            try:
                workspace_id = UUID(raw_workspace)
            except ValueError:
                workspace_id = None
        set_workspace_owner_id(workspace_id)
    else:
        set_unrestricted_view(False)
        set_workspace_owner_id(None)

    return user


async def require_super_admin(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not await is_super_admin(session, current_user.id):
        raise AppException(
            message="Permission denied.",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=["PERMISSION_DENIED", "SUPER_ADMIN_ONLY"],
        )
    return current_user


def require_permission(permission: str) -> Callable:
    async def dependency(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        uow = SqlAlchemyUserUnitOfWork(session)
        user_permissions = await uow.users.get_permissions(current_user.id)
        granted = {
            item.name
            for role in (user_permissions.roles if user_permissions else [])
            for item in role.permissions
        }

        if permission not in granted:
            raise AppException(
                message="Permission denied.",
                status_code=status.HTTP_403_FORBIDDEN,
                errors=["PERMISSION_DENIED", permission],
            )

        return current_user

    return dependency


def require_any_permission(*permissions: str) -> Callable:
    async def dependency(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        uow = SqlAlchemyUserUnitOfWork(session)
        user_permissions = await uow.users.get_permissions(current_user.id)
        granted = {
            item.name
            for role in (user_permissions.roles if user_permissions else [])
            for item in role.permissions
        }

        if not any(permission in granted for permission in permissions):
            raise AppException(
                message="Permission denied.",
                status_code=status.HTTP_403_FORBIDDEN,
                errors=["PERMISSION_DENIED", *permissions],
            )

        return current_user

    return dependency
