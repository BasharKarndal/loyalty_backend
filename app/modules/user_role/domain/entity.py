from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class Role_User:
    id: UUID
    role_id: UUID
    user_id: UUID
def update(
    self,
    user_id,
    role_id,
):
    self.user_id = user_id
    self.role_id = role_id