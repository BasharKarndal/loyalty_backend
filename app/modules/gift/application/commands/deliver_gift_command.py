from uuid import UUID

from pydantic import BaseModel


class DeliverGiftCommand(BaseModel):
    gift_type_id: UUID
