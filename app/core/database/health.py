import logging
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _sanitize_error(message: str) -> str:
    cleaned = re.sub(r"://([^:/@]+):([^@]+)@", r"://***:***@", message)
    return cleaned[:240]


async def database_health_check(session: AsyncSession) -> tuple[bool, str | None]:
    try:
        await session.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        logger.exception("Database health check failed")
        return False, _sanitize_error(f"{type(exc).__name__}: {exc}")