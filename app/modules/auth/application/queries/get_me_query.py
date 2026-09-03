from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class GetMeQuery:
    user_id: UUID
