from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.responses import ResponseBuilder
from app.core.security import Permissions, require_permission
from app.modules.gift.application.commands.deliver_gift_command import DeliverGiftCommand
from app.modules.gift.application.commands.gift_type_commands import (
    CreateGiftTypeCommand,
    UpdateGiftTypeCommand,
)
from app.modules.gift.application.commands.redeem_gift_command import RedeemGiftCommand
from app.modules.gift.application.handlers.command_handlers.create_gift_type_handler import (
    CreateGiftTypeHandler,
)
from app.modules.gift.application.handlers.command_handlers.delete_gift_type_handler import (
    DeleteGiftTypeHandler,
    RestoreGiftTypeHandler,
)
from app.modules.gift.application.handlers.command_handlers.deliver_gift_handler import (
    CancelGiftHandler,
    DeliverGiftHandler,
)
from app.modules.gift.application.handlers.command_handlers.redeem_gift_handler import (
    RedeemGiftHandler,
)
from app.modules.gift.application.handlers.command_handlers.sync_pending_gifts_handler import (
    SyncPendingGiftsHandler,
)
from app.modules.gift.application.handlers.command_handlers.update_gift_type_handler import (
    UpdateGiftTypeHandler,
)
from app.modules.gift.application.handlers.query_handlers.gift_redemption_query_handlers import (
    GetGiftRedemptionHandler,
    ListGiftRedemptionsHandler,
)
from app.modules.gift.application.handlers.query_handlers.gift_type_query_handlers import (
    GetGiftTypeHandler,
    ListGiftTypesHandler,
)
from app.modules.gift.application.queries.gift_queries import (
    GetGiftRedemptionQuery,
    GetGiftTypeQuery,
    ListGiftRedemptionsQuery,
    ListGiftTypesQuery,
)
from app.modules.gift.infrastructure.unit_of_work import SqlAlchemyGiftUnitOfWork
from app.modules.gift.presentation.responses import (
    GiftRedemptionDetailResponse,
    GiftRedemptionListResponse,
    GiftRedemptionResponse,
    GiftTypeResponse,
)
from app.modules.user.domain.entity import User
from app.shared.loyalty.resolver import resolve_loyalty_service
from app.shared.pagination import PaginationParams

gift_types_router = APIRouter(prefix="/gift-types", tags=["Gift Types"])
gifts_router = APIRouter(prefix="/gifts", tags=["Gifts"])


@gift_types_router.post("")
async def create_gift_type(
    command: CreateGiftTypeCommand,
    _: User = Depends(require_permission(Permissions.GIFT_TYPES_CREATE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = CreateGiftTypeHandler(uow)
    result = await handler.handle(command)
    return ResponseBuilder.created(
        data=GiftTypeResponse.model_validate(result),
        message="Gift type created successfully.",
    )


@gift_types_router.get("")
async def list_gift_types(
    active_only: bool | None = Query(default=None),
    _: User = Depends(require_permission(Permissions.GIFT_TYPES_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = ListGiftTypesHandler(uow)
    result = await handler.handle(ListGiftTypesQuery(active_only=active_only))
    return ResponseBuilder.success(data=[GiftTypeResponse.model_validate(item) for item in result])


@gift_types_router.get("/{gift_type_id}")
async def get_gift_type(
    gift_type_id: UUID,
    _: User = Depends(require_permission(Permissions.GIFT_TYPES_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = GetGiftTypeHandler(uow)
    result = await handler.handle(GetGiftTypeQuery(gift_type_id=gift_type_id))
    return ResponseBuilder.success(data=GiftTypeResponse.model_validate(result))


@gift_types_router.put("/{gift_type_id}")
async def update_gift_type(
    gift_type_id: UUID,
    command: UpdateGiftTypeCommand,
    _: User = Depends(require_permission(Permissions.GIFT_TYPES_UPDATE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = UpdateGiftTypeHandler(uow)
    result = await handler.handle(gift_type_id, command)
    return ResponseBuilder.success(
        data=GiftTypeResponse.model_validate(result),
        message="Gift type updated successfully.",
    )


@gift_types_router.delete("/{gift_type_id}")
async def delete_gift_type(
    gift_type_id: UUID,
    _: User = Depends(require_permission(Permissions.GIFT_TYPES_DELETE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = DeleteGiftTypeHandler(uow)
    result = await handler.handle(gift_type_id)
    return ResponseBuilder.success(
        data=GiftTypeResponse.model_validate(result),
        message="Gift type deleted successfully.",
    )


@gift_types_router.patch("/{gift_type_id}/restore")
async def restore_gift_type(
    gift_type_id: UUID,
    _: User = Depends(require_permission(Permissions.GIFT_TYPES_RESTORE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = RestoreGiftTypeHandler(uow)
    result = await handler.handle(gift_type_id)
    return ResponseBuilder.success(
        data=GiftTypeResponse.model_validate(result),
        message="Gift type restored successfully.",
    )


@gifts_router.post("/redeem")
async def redeem_gift(
    command: RedeemGiftCommand,
    current_user: User = Depends(require_permission(Permissions.GIFTS_REDEEM)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    loyalty = await resolve_loyalty_service(session, current_user.id)
    handler = RedeemGiftHandler(uow, loyalty)
    result = await handler.handle(command)
    return ResponseBuilder.created(
        data=GiftRedemptionResponse.model_validate(result),
        message="Gift redeemed successfully.",
    )


@gifts_router.post("/sync-pending")
async def sync_pending_gifts(
    current_user: User = Depends(require_permission(Permissions.GIFTS_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    loyalty = await resolve_loyalty_service(session, current_user.id)
    handler = SyncPendingGiftsHandler(uow, loyalty)
    result = await handler.handle()
    return ResponseBuilder.success(
        data=result,
        message="Pending gifts synced successfully.",
    )


@gifts_router.get("")
async def list_gifts(
    pagination: PaginationParams = Depends(),
    customer_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None, pattern="^(pending|delivered|cancelled)$"),
    exclude_cancelled: bool = Query(default=True),
    _: User = Depends(require_permission(Permissions.GIFTS_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = ListGiftRedemptionsHandler(uow)
    result = await handler.handle(
        ListGiftRedemptionsQuery(
            skip=pagination.skip,
            limit=pagination.limit,
            customer_id=customer_id,
            status=status,
            exclude_cancelled=exclude_cancelled,
        )
    )
    return ResponseBuilder.success(data=GiftRedemptionListResponse.model_validate(result))


@gifts_router.get("/{gift_id}")
async def get_gift(
    gift_id: UUID,
    _: User = Depends(require_permission(Permissions.GIFTS_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = GetGiftRedemptionHandler(uow)
    result = await handler.handle(GetGiftRedemptionQuery(redemption_id=gift_id))
    return ResponseBuilder.success(data=GiftRedemptionDetailResponse.model_validate(result))


@gifts_router.patch("/{gift_id}/deliver")
async def deliver_gift(
    gift_id: UUID,
    command: DeliverGiftCommand,
    _: User = Depends(require_permission(Permissions.GIFTS_DELIVER)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = DeliverGiftHandler(uow)
    result = await handler.handle(gift_id, command)
    return ResponseBuilder.success(
        data=GiftRedemptionResponse.model_validate(result),
        message="Gift marked as delivered.",
    )


@gifts_router.patch("/{gift_id}/cancel")
async def cancel_gift(
    gift_id: UUID,
    _: User = Depends(require_permission(Permissions.GIFTS_CANCEL)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyGiftUnitOfWork(session)
    handler = CancelGiftHandler(uow)
    result = await handler.handle(gift_id)
    return ResponseBuilder.success(
        data=GiftRedemptionResponse.model_validate(result),
        message="Gift cancelled.",
    )
