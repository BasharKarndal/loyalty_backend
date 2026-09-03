from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class Role_permission:
    id: UUID
    role_id: UUID
    permission_id: UUID
   