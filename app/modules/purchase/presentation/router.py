from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.responses import ResponseBuilder
from app.core.security import Permissions, require_permission
from app.modules.purchase.application.commands.create_purchase_command import (
    CreatePurchaseCommand,
)
from app.modules.purchase.application.commands.update_purchase_command import (
    UpdatePurchaseCommand,
)
from app.modules.purchase.application.handlers.command_handlers.create_purchase_handler import (
    CreatePurchaseHandler,
)
from app.modules.purchase.application.handlers.command_handlers.update_purchase_handler import (
    UpdatePurchaseHandler,
)
from app.modules.purchase.application.handlers.query_handlers.get_purchase_handler import (
    GetPurchaseHandler,
)
from app.modules.purchase.application.handlers.query_handlers.list_purchases_handler import (
    ListPurchasesHandler,
)
from app.modules.purchase.application.queries.purchase_queries import (
    GetPurchaseQuery,
    ListPurchasesQuery,
)
from app.modules.purchase.infrastructure.unit_of_work import SqlAlchemyPurchaseUnitOfWork
from app.modules.purchase.presentation.responses import (
    PurchaseDetailResponse,
    PurchaseListResponse,
    PurchaseResponse,
)
from app.modules.user.domain.entity import User
from app.shared.date_ranges import period_bounds
from app.shared.loyalty.resolver import resolve_loyalty_service
from app.shared.pagination import PaginationParams

router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"],
)


@router.post("")
async def create_purchase(
    command: CreatePurchaseCommand,
    current_user: User = Depends(require_permission(Permissions.PURCHASES_CREATE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyPurchaseUnitOfWork(session)
    loyalty = await resolve_loyalty_service(session, current_user.id)
    handler = CreatePurchaseHandler(uow, loyalty)
    result = await handler.handle(command)
    return ResponseBuilder.created(
        data=PurchaseResponse.model_validate(result),
        message="Purchase created successfully.",
    )


@router.get("")
async def list_purchases(
    pagination: PaginationParams = Depends(),
    customer_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    period: str | None = Query(default="all", pattern="^(all|today|week|month)$"),
    _: User = Depends(require_permission(Permissions.PURCHASES_READ)),
    session: AsyncSession = Depends(get_session),
):
    from_date, to_date = period_bounds(period)
    uow = SqlAlchemyPurchaseUnitOfWork(session)
    handler = ListPurchasesHandler(uow)
    result = await handler.handle(
        ListPurchasesQuery(
            skip=pagination.skip,
            limit=pagination.limit,
            customer_id=customer_id,
            search=search,
            from_date=from_date,
            to_date=to_date,
        )
    )
    return ResponseBuilder.success(
        data=PurchaseListResponse.model_validate(result),
    )


@router.get("/{purchase_id}")
async def get_purchase(
    purchase_id: UUID,
    _: User = Depends(require_permission(Permissions.PURCHASES_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyPurchaseUnitOfWork(session)
    handler = GetPurchaseHandler(uow)
    result = await handler.handle(GetPurchaseQuery(purchase_id=purchase_id))
    return ResponseBuilder.success(
        data=PurchaseDetailResponse.model_validate(result),
    )


@router.put("/{purchase_id}")
async def update_purchase(
    purchase_id: UUID,
    command: UpdatePurchaseCommand,
    current_user: User = Depends(require_permission(Permissions.PURCHASES_UPDATE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyPurchaseUnitOfWork(session)
    loyalty = await resolve_loyalty_service(session, current_user.id)
    handler = UpdatePurchaseHandler(uow, loyalty)
    result = await handler.handle(purchase_id, command)
    return ResponseBuilder.success(
        data=PurchaseResponse.model_validate(result),
        message="Purchase updated successfully.",
    )
