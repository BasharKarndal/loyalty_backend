from app.modules.purchase.domain.entity import Purchase
from app.modules.purchase.infrastructure.model import PurchaseModel


class PurchaseMapper:

    @staticmethod
    def to_domain(model: PurchaseModel) -> Purchase:
        return Purchase(
            id=model.id,
            customer_id=model.customer_id,
            amount=model.amount,
            points_earned=model.points_earned,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Purchase) -> PurchaseModel:
        return PurchaseModel(
            id=entity.id,
            customer_id=entity.customer_id,
            amount=entity.amount,
            points_earned=entity.points_earned,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
