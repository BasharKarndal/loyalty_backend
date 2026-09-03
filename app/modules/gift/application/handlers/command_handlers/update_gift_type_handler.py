from datetime import datetime, timezone
from uuid import UUID

from fastapi import status

from app.core.exceptions import AppException
from app.modules.gift.application.commands.gift_type_commands import UpdateGiftTypeCommand
from app.modules.gift.application.dto.gift_dto import GiftTypeDto
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork


class UpdateGiftTypeHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, gift_type_id: UUID, command: UpdateGiftTypeCommand) -> GiftTypeDto:
        gift_type = await self.uow.gift_types.get_by_id(gift_type_id)
        if gift_type is None:
            raise AppException(
                message="Gift type not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_TYPE_NOT_FOUND"],
            )

        now = datetime.now(timezone.utc)
        gift_type.update(
            name=command.name,
            icon_key=command.icon_key,
            sort_order=command.sort_order,
            updated_at=now,
        )
        await self.uow.gift_types.update(gift_type)
        await self.uow.commit()
        return GiftTypeDto.model_validate(gift_type)
