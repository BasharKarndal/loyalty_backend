"""Ensure critical schema patches exist even if a release migration was skipped."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def ensure_schema_patches(engine: AsyncEngine) -> None:
    """Idempotent DDL safety net for production deploys."""
    statements = [
        """
        ALTER TABLE purchases
        ADD COLUMN IF NOT EXISTS product_type VARCHAR(120)
        """,
    ]

    async with engine.begin() as conn:
        for sql in statements:
            try:
                await conn.execute(text(sql))
            except Exception:
                logger.exception("Schema patch failed: %s", sql.strip().splitlines()[0])
                raise

    logger.info("Schema patches verified")
