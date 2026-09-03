from app.modules.role_permission.domain.entity import Role_permission

from .model import  RolePermissionModel


class RolePermissionMapper:

    @staticmethod
    def to_domain(
        model: RolePermissionModel,
    ) -> Role_permission:

        return Role_permission(
            id=model.id,
            role_id=model.role_id,
            permission_id=model.permission_id,
        )

    @staticmethod
    def to_model(
        entity: Role_permission,
    ) -> RolePermissionModel:   

        return RolePermissionModel(
            id=entity.id,
            role_id=entity.role_id,
            permission_id=entity.permission_id,
        )
           