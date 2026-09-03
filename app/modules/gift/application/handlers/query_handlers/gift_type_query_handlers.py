from fastapi import status

from app.core.exceptions import AppException
from app.modules.gift.application.dto.gift_dto import GiftTypeDto
from app.modules.gift.application.queries.gift_queries import GetGiftTypeQuery, ListGiftTypesQuery
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork


class GetGiftTypeHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetGiftTypeQuery) -> GiftTypeDto:
        gift_type = await self.uow.gift_types.get_by_id(query.gift_type_id)
        if gift_type is None:
            raise AppException(
                message="Gift type not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_TYPE_NOT_FOUND"],
            )
        return GiftTypeDto.model_validate(gift_type)


class ListGiftTypesHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, query: ListGiftTypesQuery) -> list[GiftTypeDto]:
        items = await self.uow.gift_types.list(active_only=query.active_only)
        return [GiftTypeDto.model_validate(item) for item in items]
