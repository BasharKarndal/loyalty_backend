from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, status

from app.core.exceptions import AppException

ALLOWED_LOGO_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_LOGO_BYTES = 2 * 1024 * 1024


def uploads_root() -> Path:
    root = Path(__file__).resolve().parents[4] / "uploads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def logo_dir() -> Path:
    directory = uploads_root() / "logos"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def logo_relative_path(user_id: UUID, extension: str) -> str:
    return f"logos/{user_id}{extension}"


def logo_absolute_path(relative_path: str) -> Path:
    return uploads_root() / relative_path


def remove_logo_file(relative_path: str | None) -> None:
    if not relative_path:
        return
    path = logo_absolute_path(relative_path)
    if path.is_file():
        path.unlink()


async def save_user_logo(user_id: UUID, file: UploadFile) -> str:
    content_type = (file.content_type or "").lower()
    extension = ALLOWED_LOGO_TYPES.get(content_type)
    if extension is None:
        raise AppException(
            message="Unsupported logo format. Use PNG, JPEG, WebP, or GIF.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=["INVALID_LOGO_TYPE"],
        )

    data = await file.read()
    if len(data) > MAX_LOGO_BYTES:
        raise AppException(
            message="Logo file is too large (max 2 MB).",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=["LOGO_TOO_LARGE"],
        )

    relative = logo_relative_path(user_id, extension)
    absolute = logo_dir() / f"{user_id}{extension}"
    absolute.write_bytes(data)
    return relative
