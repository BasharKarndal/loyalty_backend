from app.modules.role.domain.entity import Role

from .model import RoleModel


class RoleMapper:

    @staticmethod
    def to_domain(
        model: RoleModel,
    ) -> Role:

        return Role(
            id=model.id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
        )

    @staticmethod
    def to_model(
        entity: Role,
    ) -> RoleModel:

        return RoleModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )