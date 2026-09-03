from contextvars import ContextVar
from uuid import UUID

from sqlalchemy import ColumnElement, false as sql_false, true as sql_true

SUPER_ADMIN_ROLE = "super_admin"
ADMIN_ROLE = "admin"

_current_owner_id: ContextVar[UUID | None] = ContextVar("current_owner_id", default=None)
_unrestricted_view: ContextVar[bool] = ContextVar("unrestricted_view", default=False)
_workspace_owner_id: ContextVar[UUID | None] = ContextVar("workspace_owner_id", default=None)


def set_current_owner_id(owner_id: UUID | None) -> None:
    _current_owner_id.set(owner_id)


def get_current_owner_id() -> UUID | None:
    return _current_owner_id.get()


def set_unrestricted_view(enabled: bool) -> None:
    _unrestricted_view.set(enabled)


def is_unrestricted_view() -> bool:
    return _unrestricted_view.get()


def set_workspace_owner_id(owner_id: UUID | None) -> None:
    _workspace_owner_id.set(owner_id)


def get_workspace_owner_id() -> UUID | None:
    return _workspace_owner_id.get()


def effective_owner_id() -> UUID | None:
    return _workspace_owner_id.get() or _current_owner_id.get()


def require_owner_id() -> UUID:
    owner_id = effective_owner_id()
    if owner_id is None:
        raise RuntimeError("Tenant owner context is not set.")
    return owner_id


def can_access_owner(owner_id: UUID) -> bool:
    if is_unrestricted_view():
        workspace = get_workspace_owner_id()
        return workspace is None or workspace == owner_id
    current = get_current_owner_id()
    return current is not None and current == owner_id


def owner_match(column) -> ColumnElement[bool]:
    if is_unrestricted_view():
        workspace = get_workspace_owner_id()
        if workspace is None:
            return sql_true()
        return column == workspace
    owner_id = get_current_owner_id()
    if owner_id is None:
        return sql_false()
    return column == owner_id
