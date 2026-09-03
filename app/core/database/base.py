# app/core/database/base.py

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app.core.database.naming_convention import NAMING_CONVENTION


metadata = MetaData(
    naming_convention=NAMING_CONVENTION
)


class Base(DeclarativeBase):
    metadata = metadata