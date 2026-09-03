from app.modules.settings.domain.entity import UserSettings
from app.modules.settings.infrastructure.model import UserSettingsModel


class UserSettingsMapper:

    @staticmethod
    def to_domain(model: UserSettingsModel) -> UserSettings:
        return UserSettings(
            id=model.id,
            user_id=model.user_id,
            cafe_name=model.cafe_name,
            logo_path=model.logo_path,
            currency=model.currency,
            visit_reward_target=model.visit_reward_target,
            points_reward_target=model.points_reward_target,
            currency_per_point=model.currency_per_point,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: UserSettings) -> UserSettingsModel:
        return UserSettingsModel(
            id=entity.id,
            user_id=entity.user_id,
            cafe_name=entity.cafe_name,
            logo_path=entity.logo_path,
            currency=entity.currency,
            visit_reward_target=entity.visit_reward_target,
            points_reward_target=entity.points_reward_target,
            currency_per_point=entity.currency_per_point,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
