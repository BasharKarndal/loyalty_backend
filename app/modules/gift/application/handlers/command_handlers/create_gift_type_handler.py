from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.core.exceptions import AppException
from app.modules.gift.application.commands.gift_type_commands import CreateGiftTypeCommand
from app.modules.gift.application.dto.gift_dto import GiftTypeDto
from app.modules.gift.domain.gift_type_entity import GiftType
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork
from app.shared.tenancy import require_owner_id


class CreateGiftTypeHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, command: CreateGiftTypeCommand) -> GiftTypeDto:
        now = datetime.now(timezone.utc)
        gift_type = GiftType(
            id=uuid4(),
            owner_id=require_owner_id(),
            name=command.name.strip(),
            icon_key=command.icon_key.strip() or "card_giftcard",
            sort_order=command.sort_order,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        await self.uow.gift_types.add(gift_type)
        await self.uow.commit()
        return GiftTypeDto.model_validate(gift_type)
