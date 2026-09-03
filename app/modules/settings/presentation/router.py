from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import AppException
from app.core.responses import ResponseBuilder
from app.core.security import get_current_user
from app.modules.settings.application.dto.settings_dto import UpdateUserSettingsCommand
from app.modules.settings.application.user_settings_service import UserSettingsService
from app.modules.settings.infrastructure.logo_storage import (
    logo_absolute_path,
    remove_logo_file,
    save_user_logo,
)
from app.modules.settings.infrastructure.repository import SqlAlchemyUserSettingsRepository
from app.modules.settings.presentation.responses import UserSettingsResponse
from app.modules.user.domain.entity import User

router = APIRouter(prefix="/settings", tags=["Settings"])


def _service(session: AsyncSession) -> UserSettingsService:
    return UserSettingsService(SqlAlchemyUserSettingsRepository(session))


@router.get("/me")
async def get_my_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = _service(session)
    settings = await service.get_or_create(current_user.id)
    await session.commit()
    return ResponseBuilder.success(
        data=UserSettingsResponse.model_validate(service.to_dto(settings)),
    )


@router.put("/me")
async def update_my_settings(
    command: UpdateUserSettingsCommand,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = _service(session)
    settings = await service.get_or_create(current_user.id)
    now = datetime.now(timezone.utc)
    settings.update(
        cafe_name=command.cafe_name,
        currency=command.currency,
        visit_reward_target=command.visit_reward_target,
        points_reward_target=command.points_reward_target,
        currency_per_point=command.currency_per_point,
        updated_at=now,
    )
    await service.repository.update(settings)
    await session.commit()
    return ResponseBuilder.success(
        data=UserSettingsResponse.model_validate(service.to_dto(settings)),
        message="Settings updated successfully.",
    )


@router.post("/me/logo")
async def upload_my_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = _service(session)
    settings = await service.get_or_create(current_user.id)

    remove_logo_file(settings.logo_path)
    relative = await save_user_logo(current_user.id, file)
    now = datetime.now(timezone.utc)
    settings.set_logo(relative, now)
    await service.repository.update(settings)
    await session.commit()

    return ResponseBuilder.success(
        data=UserSettingsResponse.model_validate(service.to_dto(settings)),
        message="Logo uploaded successfully.",
    )


@router.delete("/me/logo")
async def delete_my_logo(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = _service(session)
    settings = await service.get_or_create(current_user.id)

    remove_logo_file(settings.logo_path)
    now = datetime.now(timezone.utc)
    settings.set_logo(None, now)
    await service.repository.update(settings)
    await session.commit()

    return ResponseBuilder.success(
        data=UserSettingsResponse.model_validate(service.to_dto(settings)),
        message="Logo removed successfully.",
    )


@router.get("/me/logo")
async def get_my_logo(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = _service(session)
    settings = await service.get_or_create(current_user.id)
    await session.commit()

    if not settings.logo_path:
        raise AppException(
            message="Logo not found.",
            status_code=404,
            errors=["LOGO_NOT_FOUND"],
        )

    path = logo_absolute_path(settings.logo_path)
    if not path.is_file():
        raise AppException(
            message="Logo file missing.",
            status_code=404,
            errors=["LOGO_NOT_FOUND"],
        )

    return FileResponse(path)
