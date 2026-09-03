import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def database_health_check(session: AsyncSession) -> bool:
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database health check failed")
        return False