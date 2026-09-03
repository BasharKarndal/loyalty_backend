from app.modules.Permission.domain.entity import Permission


from .model import PermissionModel


class PermissionMapper:

    @staticmethod
    def to_domain(
        model: PermissionModel,
    ) -> Permission :

        return Permission(
            id=model.id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
        )

    @staticmethod
    def to_model(
        entity: Permission,
    ) -> PermissionModel:

        return PermissionModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )