from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUserDep, DbDep
from app.schemas.media import FileInSchema, FileOutSchema
from app.services.media import (
    add_user_media,
    batch_add_user_media,
    delete_user_media,
    get_user_media,
)

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=list[FileOutSchema])
async def get_media(db: DbDep, user_id: UUID):
    """Fetches media files associated with a user."""
    media = await get_user_media(db, user_id)
    return media


@router.post("/batch-add", response_model=list[FileOutSchema])
async def batch_add_media(
    db: DbDep, current_user: CurrentUserDep, files_data: list[FileInSchema]
):
    """Adds multiple media files to a user."""
    if not files_data:
        raise HTTPException(status_code=400, detail="No files provided")

    try:
        files = await batch_add_user_media(db, current_user.id, files_data)
        return files
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=FileOutSchema)
async def add_media(db: DbDep, current_user: CurrentUserDep, file_data: FileInSchema):
    """Adds media files to a user."""
    try:
        file = await add_user_media(db, current_user.id, file_data)
        return file
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{file_id}")
async def delete_media(db: DbDep, current_user: CurrentUserDep, file_id: int):
    """Deletes a media file associated with a user."""
    try:
        await delete_user_media(db, current_user.id, file_id)
        return {"detail": "Media file deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
