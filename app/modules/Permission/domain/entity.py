from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class Permission:
    id: UUID
    name: str
    description: str | None = None
    is_active: bool = True

    def update(
        self,
        name: str,
        description: str | None,
        is_active: bool,
    ) -> None:
        self.name = name
        self.description = description
        self.is_active = is_active

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False