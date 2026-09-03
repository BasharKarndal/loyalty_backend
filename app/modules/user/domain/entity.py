from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class User:
    id: UUID
    username: str
    full_name: str
    email: str
    password_hash: str
    phone: str | None = None
    national_id: str | None = None
    is_active: bool = True

    def update(
        self,
        full_name: str,
        email: str,
        phone: str | None,
        national_id: str | None,
        is_active: bool,
    ) -> None:
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.national_id = national_id
        self.is_active = is_active

    def change_password(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
