"""
seed_super_admin.py
-------------------
ينشئ:
  1. كل الصلاحيات الموجودة في Permissions
  2. دور super_admin مربوط بكل الصلاحيات
  3. مستخدم admin مربوط بـ super_admin

يُشغَّل:
    python scripts/seed_super_admin.py
"""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from uuid import uuid4

from sqlalchemy import select

from app.core.database.session import AsyncSessionLocal
from app.core.security.hashing import PasswordHasher
from app.core.security.permissions import Permissions
from app.modules.Permission.infrastructure.model import PermissionModel
from app.modules.role.infrastructure.model import RoleModel
from app.modules.role_permission.infrastructure.model import RolePermissionModel
from app.modules.user.infrastructure.model import UserModel
from app.modules.user_role.infrastructure.model import UserRoleModel

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@1234"
ADMIN_FULL_NAME = "Super Admin"
ADMIN_EMAIL = "admin@local"
SUPER_ADMIN_ROLE = "super_admin"


def all_permission_names() -> list[str]:
    return [
        value
        for name, value in vars(Permissions).items()
        if name.isupper() and isinstance(value, str)
    ]


async def ensure_permission(
    session, permission_map: dict[str, PermissionModel], perm_name: str
) -> PermissionModel:
    if perm_name in permission_map:
        return permission_map[perm_name]

    result = await session.execute(
        select(PermissionModel).where(PermissionModel.name == perm_name)
    )
    perm = result.scalar_one_or_none()
    if perm is None:
        perm = PermissionModel(
            id=uuid4(),
            name=perm_name,
            description=perm_name.replace(".", " ").replace("_", " ").title(),
            is_active=True,
        )
        session.add(perm)
        print(f"  + permission: {perm_name}")
    else:
        print(f"  . permission exists: {perm_name}")

    permission_map[perm_name] = perm
    return perm


async def ensure_role(session, name: str, description: str) -> RoleModel:
    result = await session.execute(select(RoleModel).where(RoleModel.name == name))
    role = result.scalar_one_or_none()
    if role is None:
        role = RoleModel(
            id=uuid4(),
            name=name,
            description=description,
            is_active=True,
        )
        session.add(role)
        print(f"  + role: {name}")
    else:
        role.description = description
        role.is_active = True
        print(f"  . role exists: {name}")
    await session.flush()
    return role


async def sync_role_permissions(
    session,
    role: RoleModel,
    permission_map: dict[str, PermissionModel],
    permission_names: list[str],
) -> None:
    desired = set(permission_names)

    existing = (
        await session.execute(
            select(RolePermissionModel).where(RolePermissionModel.role_id == role.id)
        )
    ).scalars().all()

    existing_by_perm_id = {link.permission_id: link for link in existing}
    desired_perm_ids = {permission_map[name].id for name in desired if name in permission_map}

    for perm_name in desired:
        perm = permission_map.get(perm_name)
        if perm is None:
            continue
        if perm.id not in existing_by_perm_id:
            session.add(
                RolePermissionModel(
                    id=uuid4(),
                    role_id=role.id,
                    permission_id=perm.id,
                )
            )
            print(f"  + role_permission: {role.name} -> {perm_name}")

    for perm_id, link in existing_by_perm_id.items():
        if perm_id not in desired_perm_ids:
            await session.delete(link)
            print(f"  - role_permission removed from {role.name}")


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        print("\n== Permissions ==")
        permission_map: dict[str, PermissionModel] = {}
        permission_names = all_permission_names()
        for perm_name in permission_names:
            await ensure_permission(session, permission_map, perm_name)
        await session.flush()

        print("\n== Roles ==")
        super_role = await ensure_role(session, SUPER_ADMIN_ROLE, "System administrator")
        await sync_role_permissions(
            session,
            super_role,
            permission_map,
            permission_names,
        )

        admin_permissions = [
            name
            for name in permission_names
            if name.startswith(("customers.", "purchases.", "gift_types.", "gifts."))
        ]
        cafe_role = await ensure_role(session, "admin", "Cafe tenant administrator")
        await sync_role_permissions(
            session,
            cafe_role,
            permission_map,
            admin_permissions,
        )

        print("\n== Super admin user ==")
        result = await session.execute(
            select(UserModel).where(UserModel.username == ADMIN_USERNAME)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = UserModel(
                id=uuid4(),
                username=ADMIN_USERNAME,
                full_name=ADMIN_FULL_NAME,
                email=ADMIN_EMAIL,
                password_hash=PasswordHasher.hash(ADMIN_PASSWORD),
                is_active=True,
            )
            session.add(user)
            print(f"  + user: {ADMIN_USERNAME}")
        else:
            print(f"  . user exists: {ADMIN_USERNAME}")
        await session.flush()

        result = await session.execute(
            select(UserRoleModel).where(
                UserRoleModel.user_id == user.id,
                UserRoleModel.role_id == super_role.id,
            )
        )
        if result.scalar_one_or_none() is None:
            session.add(
                UserRoleModel(
                    id=uuid4(),
                    user_id=user.id,
                    role_id=super_role.id,
                )
            )
            print(f"  + user_role: {ADMIN_USERNAME} -> {SUPER_ADMIN_ROLE}")

        await session.commit()
        print("\nSeed completed successfully!")
        print(f"  role     : {SUPER_ADMIN_ROLE} ({len(permission_names)} permissions)")
        print(f"  cafe role: admin ({len(admin_permissions)} permissions)")
        print(f"  username : {ADMIN_USERNAME}")
        print(f"  password : {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
