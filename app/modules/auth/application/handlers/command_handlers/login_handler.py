from fastapi import status

from app.core.exceptions import AppException
from app.core.security.hashing import PasswordHasher
from app.core.security.jwt import create_access_token
from app.modules.auth.application.commands.login_command import LoginCommand
from app.modules.auth.application.dto.token_dto import TokenDto
from app.modules.user.domain.unit_of_work import UserUnitOfWork
from app.shared.access import assert_workspace_access


class LoginHandler:

    def __init__(self, uow: UserUnitOfWork, session):
        self.uow = uow
        self.session = session

    async def handle(self, command: LoginCommand) -> TokenDto:
        user = await self.uow.users.get_by_username(command.username)

        if user is None:
            raise AppException(
                message="Invalid username or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                errors=["INVALID_CREDENTIALS"],
            )

        if not PasswordHasher.verify(command.password, user.password_hash):
            raise AppException(
                message="Invalid username or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                errors=["INVALID_CREDENTIALS"],
            )

        if not user.is_active:
            raise AppException(
                message="User account is inactive.",
                status_code=status.HTTP_403_FORBIDDEN,
                errors=["USER_INACTIVE"],
            )

        await assert_workspace_access(self.session, user)

        token = create_access_token(data={"sub": str(user.id)})

        return TokenDto(access_token=token)
