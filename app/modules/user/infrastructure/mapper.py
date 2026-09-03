from app.modules.user.domain.entity import User
from app.modules.user.infrastructure.model import UserModel


class UserMapper:

    @staticmethod
    def to_domain(user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            username=user_model.username,
            full_name=user_model.full_name,
            email=user_model.email,
            password_hash=user_model.password_hash,
            phone=user_model.phone,
            national_id=user_model.national_id,
            is_active=user_model.is_active,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            full_name=entity.full_name,
            email=entity.email,
            password_hash=entity.password_hash,
            phone=entity.phone,
            national_id=entity.national_id,
            is_active=entity.is_active,
        )
