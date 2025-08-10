from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.models.file import File, UserMedia
from app.schemas.media import FileInSchema


async def get_user_media(db: AsyncSession, user_id: UUID):
    """Fetches media files associated with a user."""
    result = await db.scalars(
        select(File)
        .join(UserMedia, UserMedia.file_id == File.id)
        .where(UserMedia.user_id == user_id)
        .options(joinedload(File.thumbnail)),
    )
    return result.all()


async def add_user_media(db: AsyncSession, user_id: UUID, file_data: FileInSchema):
    """Adds media files to a user."""
    try:
        # with_for_update() prevents race conditions
        result = await db.scalars(
            select(UserMedia).where(UserMedia.user_id == user_id).with_for_update(),
        )
        if len(result.all()) >= settings.MAX_USER_MEDIA_FILES:
            raise ValueError("User has reached the maximum number of media files")

        file = File(**file_data.model_dump())
        db.add(file)
        await db.flush()

        user_media = UserMedia(user_id=user_id, file_id=file.id)
        db.add(user_media)
        await db.commit()

        return file
    except Exception as e:
        await db.rollback()
        raise e


async def batch_add_user_media(
    db: AsyncSession, user_id: UUID, files_data: list[FileInSchema],
):
    """Adds multiple media files to a user."""
    try:
        result = await db.scalars(
            select(UserMedia).where(UserMedia.user_id == user_id).with_for_update(),
        )
        if len(result.all()) + len(files_data) > settings.MAX_USER_MEDIA_FILES:
            raise ValueError("User has reached the maximum number of media files")

        files = [File(**file_data.model_dump()) for file_data in files_data]
        db.add_all(files)
        await db.flush()

        user_media = [UserMedia(user_id=user_id, file_id=file.id) for file in files]
        db.add_all(user_media)
        await db.commit()

        return files
    except Exception as e:
        await db.rollback()
        raise e


async def remove_user_media(db: AsyncSession, user_id: UUID, file_id: UUID):
    """Removes a media file from a user."""
    try:
        user_media = await db.scalar(
            select(UserMedia).where(
                UserMedia.user_id == user_id, UserMedia.file_id == file_id,
            ),
        )
        if not user_media:
            raise ValueError("User media not found")

        await db.delete(user_media)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_user_media(db: AsyncSession, user_id: UUID, file_id: int):
    """Deletes a media file associated with a user."""
    try:
        user_file = await db.scalar(
            select(UserMedia).where(
                UserMedia.user_id == user_id, UserMedia.file_id == file_id,
            ),
        )
        if not user_file:
            raise ValueError("User media not found")

        file = await db.scalar(select(File).where(File.id == file_id))
        if file:
            await db.delete(file)
            await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
