from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.responses import ResponseBuilder
from app.core.security import get_current_user
from app.modules.auth.application.commands.login_command import LoginCommand
from app.modules.auth.application.handlers.command_handlers.login_handler import (
    LoginHandler,
)
from app.modules.auth.application.handlers.query_handlers.get_me_handler import (
    GetMeHandler,
)
from app.modules.auth.application.queries.get_me_query import GetMeQuery
from app.modules.auth.presentation.responses import MeResponse, TokenResponse
from app.modules.user.domain.entity import User
from app.modules.user.infrastructure.unit_of_work import SqlAlchemyUserUnitOfWork

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/login")
async def login(
    command: LoginCommand,
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyUserUnitOfWork(session)
    handler = LoginHandler(uow, session)
    token = await handler.handle(command)
    return ResponseBuilder.success(
        data=TokenResponse.model_validate(token),
        message="Login successful.",
    )


@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyUserUnitOfWork(session)
    handler = GetMeHandler(uow, session)
    result = await handler.handle(GetMeQuery(user_id=current_user.id))
    return ResponseBuilder.success(
        data=MeResponse.model_validate(result),
    )
