from logging.config import fileConfig
import asyncio

from alembic import context

from sqlalchemy.ext.asyncio import (
    async_engine_from_config,
)

from sqlalchemy.pool import NullPool


from app.core.config.settings import settings
from app.core.database.base import Base

# مهم: تحميل جميع الـ models حتى تظهر في metadata

from app.modules.role.infrastructure.model import RoleModel
from app.modules.Permission.infrastructure.model import PermissionModel
from app.modules.user.infrastructure.model import UserModel
from app.modules.role_permission.infrastructure.model import RolePermissionModel
from app.modules.user_role.infrastructure.model import UserRoleModel
from app.modules.customer.infrastructure.model import CustomerModel
from app.modules.gift.infrastructure.model import GiftRedemptionModel, GiftTypeModel
from app.modules.purchase.infrastructure.model import PurchaseModel
from app.modules.settings.infrastructure.model import UserSettingsModel
from app.modules.subscription.infrastructure.model import SubscriptionModel



# Alembic Config object
config = context.config


# استخدام اتصال async
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)


# إعداد logging
if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


# Metadata المستخدمة في autogenerate
target_metadata = Base.metadata


print(
    "Loaded tables:",
    target_metadata.tables.keys()
)


def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()



def do_run_migrations(connection):

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()



async def run_async_migrations():

    connectable = async_engine_from_config(
        config.get_section(
            config.config_ini_section
        ),
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )


    async with connectable.connect() as connection:

        await connection.run_sync(
            do_run_migrations
        )


    await connectable.dispose()



def run_migrations_online():

    asyncio.run(
        run_async_migrations()
    )



if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
