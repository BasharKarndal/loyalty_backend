from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.responses import ResponseBuilder
from app.core.security import Permissions, require_permission
from app.modules.customer.application.commands.create_customer_command import (
    CreateCustomerCommand,
)
from app.modules.customer.application.commands.update_customer_command import (
    UpdateCustomerCommand,
)
from app.modules.customer.application.handlers.command_handlers.create_customer_handler import (
    CreateCustomerHandler,
)
from app.modules.customer.application.handlers.command_handlers.delete_customer_handler import (
    DeleteCustomerHandler,
)
from app.modules.customer.application.handlers.command_handlers.restore_customer_handler import (
    RestoreCustomerHandler,
)
from app.modules.customer.application.handlers.command_handlers.update_customer_handler import (
    UpdateCustomerHandler,
)
from app.modules.customer.application.handlers.query_handlers.get_customer_handler import (
    GetCustomerHandler,
)
from app.modules.customer.application.handlers.query_handlers.list_customers_handler import (
    ListCustomersHandler,
)
from app.modules.customer.application.queries.customer_queries import (
    GetCustomerQuery,
    ListCustomersQuery,
)
from app.modules.customer.infrastructure.unit_of_work import SqlAlchemyCustomerUnitOfWork
from app.modules.customer.presentation.responses import (
    CustomerListResponse,
    CustomerResponse,
)
from app.modules.user.domain.entity import User
from app.shared.pagination import PaginationParams

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post("")
async def create_customer(
    command: CreateCustomerCommand,
    _: User = Depends(require_permission(Permissions.CUSTOMERS_CREATE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyCustomerUnitOfWork(session)
    handler = CreateCustomerHandler(uow)
    result = await handler.handle(command)
    return ResponseBuilder.created(
        data=CustomerResponse.model_validate(result),
        message="Customer created successfully.",
    )


@router.get("")
async def list_customers(
    pagination: PaginationParams = Depends(),
    search: str | None = Query(default=None, max_length=100),
    active_only: bool = Query(default=True),
    inactive_only: bool = Query(default=False),
    _: User = Depends(require_permission(Permissions.CUSTOMERS_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyCustomerUnitOfWork(session)
    handler = ListCustomersHandler(uow)
    result = await handler.handle(
        ListCustomersQuery(
            skip=pagination.skip,
            limit=pagination.limit,
            search=search,
            active_only=active_only,
            inactive_only=inactive_only,
        )
    )
    return ResponseBuilder.success(
        data=CustomerListResponse.model_validate(result),
    )


@router.get("/{customer_id}")
async def get_customer(
    customer_id: UUID,
    _: User = Depends(require_permission(Permissions.CUSTOMERS_READ)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyCustomerUnitOfWork(session)
    handler = GetCustomerHandler(uow)
    result = await handler.handle(GetCustomerQuery(customer_id=customer_id))
    return ResponseBuilder.success(
        data=CustomerResponse.model_validate(result),
    )


@router.put("/{customer_id}")
async def update_customer(
    customer_id: UUID,
    command: UpdateCustomerCommand,
    _: User = Depends(require_permission(Permissions.CUSTOMERS_UPDATE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyCustomerUnitOfWork(session)
    handler = UpdateCustomerHandler(uow)
    result = await handler.handle(customer_id, command)
    return ResponseBuilder.success(
        data=CustomerResponse.model_validate(result),
        message="Customer updated successfully.",
    )


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: UUID,
    _: User = Depends(require_permission(Permissions.CUSTOMERS_DELETE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyCustomerUnitOfWork(session)
    handler = DeleteCustomerHandler(uow)
    await handler.handle(customer_id)
    return ResponseBuilder.deleted(message="Customer deleted successfully.")


@router.patch("/{customer_id}/restore")
async def restore_customer(
    customer_id: UUID,
    _: User = Depends(require_permission(Permissions.CUSTOMERS_RESTORE)),
    session: AsyncSession = Depends(get_session),
):
    uow = SqlAlchemyCustomerUnitOfWork(session)
    handler = RestoreCustomerHandler(uow)
    result = await handler.handle(customer_id)
    return ResponseBuilder.success(
        data=CustomerResponse.model_validate(result),
        message="Customer restored successfully.",
    )
