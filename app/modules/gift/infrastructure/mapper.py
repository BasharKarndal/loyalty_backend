from app.modules.gift.domain.gift_redemption_entity import GiftRedemption
from app.modules.gift.domain.gift_type_entity import GiftType
from app.modules.gift.infrastructure.model import GiftRedemptionModel, GiftTypeModel


class GiftTypeMapper:

    @staticmethod
    def to_domain(model: GiftTypeModel) -> GiftType:
        return GiftType(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            icon_key=model.icon_key,
            sort_order=model.sort_order,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: GiftType) -> GiftTypeModel:
        return GiftTypeModel(
            id=entity.id,
            owner_id=entity.owner_id,
            name=entity.name,
            icon_key=entity.icon_key,
            sort_order=entity.sort_order,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class GiftRedemptionMapper:

    @staticmethod
    def to_domain(model: GiftRedemptionModel) -> GiftRedemption:
        return GiftRedemption(
            id=model.id,
            customer_id=model.customer_id,
            gift_type_id=model.gift_type_id,
            gift_type_name=model.gift_type_name,
            gift_type_icon=model.gift_type_icon,
            points_used=model.points_used,
            reward_track=model.reward_track,
            notes=model.notes,
            status=model.status,
            created_at=model.created_at,
            delivered_at=model.delivered_at,
            updated_at=model.updated_at,
            balance_deducted=bool(getattr(model, "balance_deducted", False)),
        )

    @staticmethod
    def to_model(entity: GiftRedemption) -> GiftRedemptionModel:
        return GiftRedemptionModel(
            id=entity.id,
            customer_id=entity.customer_id,
            gift_type_id=entity.gift_type_id,
            gift_type_name=entity.gift_type_name,
            gift_type_icon=entity.gift_type_icon,
            points_used=entity.points_used,
            reward_track=entity.reward_track,
            notes=entity.notes,
            status=entity.status,
            balance_deducted=entity.balance_deducted,
            delivered_at=entity.delivered_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
