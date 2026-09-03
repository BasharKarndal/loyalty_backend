from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class PermissionDto:

    id: UUID
    name: str



@dataclass(slots=True)
class RolePermissionsDto:

    id: UUID
    name: str
    permissions: list[PermissionDto]



@dataclass(slots=True)
class UserPermissionsDto:

    user_id: UUID
    username: str
    roles: list[RolePermissionsDto]