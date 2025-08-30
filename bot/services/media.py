import logging
from uuid import UUID

import httpx
from aiogram.utils.i18n import gettext as _

from bot.http_client import get_http_client_manager
from bot.schemas.media import FileSchema

logger = logging.getLogger(__name__)


async def get_media(user_id: UUID) -> list[FileSchema]:
    """Fetch media files for a user.

    Args:
        user_id: UUID of the user whose media to fetch

    Returns:
        list[FileSchema]: List of user's media files

    Raises:
        ValueError: If API call fails or user not found

    """
    try:
        http_client = get_http_client_manager()
        response = await http_client.get(
            "/v1/media",
            params={"user_id": str(user_id)},
        )
        media_list = [FileSchema.model_validate(file) for file in response.json()]

        logger.debug(f"Fetched {len(media_list)} media files for user {user_id}")
        return media_list

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.info(f"No media found for user {user_id}")
            return []
        if e.response.status_code == 400:
            logger.warning(f"Invalid user ID for media request: {user_id}")
            raise ValueError(_("Invalid user ID provided"))
        if e.response.status_code == 401:
            logger.warning("Authentication failed for media request")
            raise ValueError(_("Authentication failed. Please try again."))
        if e.response.status_code == 403:
            logger.warning(f"Access forbidden for media of user {user_id}")
            raise ValueError(_("Access denied. Unable to fetch media."))
        logger.error(f"HTTP error fetching media for user {user_id}: {e}")
        raise ValueError(
            _("Unable to fetch media files. Please try again later."),
        )

    except httpx.RequestError as e:
        logger.error(f"Network error fetching media for user {user_id}: {e}")
        raise ValueError(_("Network error. Please check your connection."))

    except ValueError as e:
        # Re-raise validation errors from FileSchema
        logger.error(f"Media validation error for user {user_id}: {e}")
        raise ValueError(_("Invalid media data received from server."))

    except Exception as e:
        logger.error(f"Unexpected error fetching media for user {user_id}: {e}")
        raise ValueError(_("An unexpected error occurred. Please try again."))


async def get_user_media(telegram_user_id: int) -> list[FileSchema]:
    """Fetch media files for the current authenticated user.

    Args:
        telegram_user_id: Telegram user ID

    Returns:
        list[FileSchema]: List of user's media files

    Raises:
        ValueError: If API call fails or authentication error

    """
    try:
        # Get current user first to get their UUID
        from bot.services.user import get_current_user

        user = await get_current_user(telegram_user_id)
        media_list = await get_media(user.id)

        logger.debug(
            f"Fetched {len(media_list)} media files for telegram user {telegram_user_id}",
        )
        return media_list

    except ValueError:
        # Re-raise user service or media service errors
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error fetching user media for {telegram_user_id}: {e}",
        )
        raise ValueError(_("An unexpected error occurred. Please try again."))


def validate_media_list(media_list: list[FileSchema]) -> bool:
    """Validate a list of media files.

    Args:
        media_list: List of media files to validate

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValueError: If validation fails with specific error message

    """
    if not media_list:
        raise ValueError(_("At least one media file is required"))

    if len(media_list) > 10:  # Max from bot config
        raise ValueError(_("Too many media files. Maximum 10 allowed."))

    # Check for duplicate file IDs
    file_ids = [media.file_id for media in media_list if media.file_id]
    if len(file_ids) != len(set(file_ids)):
        raise ValueError(_("Duplicate media files detected"))

    # Validate individual files
    for media in media_list:
        if not media.file_id:
            raise ValueError(_("Media file missing file ID"))

        # Basic file type validation
        if media.file_type not in ["image", "video", "audio", "document", "other"]:
            raise ValueError(
                _("Invalid file type: {type}").format(type=media.file_type),
            )

    logger.debug(f"Validated {len(media_list)} media files successfully")
    return True
