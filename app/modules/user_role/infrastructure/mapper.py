from app.modules.user_role.domain.entity import Role_User

from .model import UserRoleModel


class UserRoleMapper:

    @staticmethod
    def to_domain(
        model: UserRoleModel,
    ) -> Role_User:

        return Role_User(
            id=model.id,
            user_id=model.user_id,
            role_id=model.role_id,
        )


    @staticmethod
    def to_model(
        entity: Role_User,
    ) -> UserRoleModel:

        return UserRoleModel(
            id=entity.id,
            user_id=entity.user_id,
            role_id=entity.role_id,
        )