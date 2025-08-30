import logging
from uuid import UUID

import httpx
from aiogram.utils.i18n import gettext as _

from bot.http_client import get_http_client_manager
from bot.schemas.user import UserSchema, UserUpdateSchema

logger = logging.getLogger(__name__)


async def get_user(user_id: UUID) -> UserSchema:
    """Get a user by ID.

    Args:
        user_id: UUID of the user to fetch

    Returns:
        UserSchema: The user data

    Raises:
        ValueError: If user not found or other API error

    """
    try:
        http_client = get_http_client_manager()
        response = await http_client.get(f"/v1/users/{user_id}")
        user_data = UserSchema.model_validate(response.json())

        logger.debug(f"User {user_id} fetched from API")
        return user_data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"User {user_id} not found")
            raise ValueError(_("User not found"))
        if e.response.status_code == 403:
            logger.warning(f"Access forbidden for user {user_id}")
            raise ValueError(_("Access denied"))
        logger.error(f"HTTP error fetching user {user_id}: {e}")
        raise ValueError(
            _("Unable to fetch user data. Please try again later."),
        )

    except httpx.RequestError as e:
        logger.error(f"Network error fetching user {user_id}: {e}")
        raise ValueError(_("Network error. Please check your connection."))

    except Exception as e:
        logger.error(f"Unexpected error fetching user {user_id}: {e}")
        raise ValueError(_("An unexpected error occurred. Please try again."))


async def get_current_user(telegram_id: int) -> UserSchema:
    """Get the current user.

    Args:
        telegram_id: Telegram user ID

    Returns:
        UserSchema: The current user data

    Raises:
        ValueError: If user not found or other API error

    """
    try:
        http_client = get_http_client_manager()
        response = await http_client.get(
            "/v1/users/me",
            telegram_user_id=telegram_id,
        )
        user_data = UserSchema.model_validate(response.json())

        logger.debug(f"Current user {telegram_id} fetched from API")
        return user_data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"Current user {telegram_id} not found")
            raise ValueError(
                _("Your account was not found. Please register again."),
            )
        if e.response.status_code == 401:
            logger.warning(f"Authentication failed for user {telegram_id}")
            raise ValueError(_("Authentication failed. Please try again."))
        if e.response.status_code == 403:
            logger.warning(f"Access forbidden for user {telegram_id}")
            raise ValueError(_("Your account has been restricted."))
        logger.error(f"HTTP error fetching current user {telegram_id}: {e}")
        raise ValueError(
            _("Unable to fetch your profile. Please try again later."),
        )

    except httpx.RequestError as e:
        logger.error(f"Network error fetching current user {telegram_id}: {e}")
        raise ValueError(_("Network error. Please check your connection."))

    except Exception as e:
        logger.error(f"Unexpected error fetching current user {telegram_id}: {e}")
        raise ValueError(_("An unexpected error occurred. Please try again."))


async def update_user(
    telegram_id: int,
    user_data: UserUpdateSchema,
) -> UserSchema:
    """Update user data.

    Args:
        telegram_id: Telegram user ID
        user_data: Updated user data

    Returns:
        UserSchema: The updated user data

    Raises:
        ValueError: If update fails or validation error

    """
    try:
        http_client = get_http_client_manager()
        response = await http_client.put(
            "/v1/users/me",
            telegram_user_id=telegram_id,
            json=user_data.model_dump(exclude_unset=True, mode="json"),
        )
        updated_user = UserSchema.model_validate(response.json())

        logger.info(f"User {telegram_id} updated successfully")
        return updated_user

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            logger.warning(
                f"Validation error updating user {telegram_id}: {e.response.text}",
            )
            raise ValueError(_("Invalid data provided. Please check your input."))
        if e.response.status_code == 401:
            logger.warning(f"Authentication failed for user {telegram_id}")
            raise ValueError(_("Authentication failed. Please try again."))
        if e.response.status_code == 403:
            logger.warning(f"Access forbidden for user {telegram_id}")
            raise ValueError(_("You don't have permission to perform this action."))
        if e.response.status_code == 404:
            logger.warning(f"User {telegram_id} not found during update")
            raise ValueError(
                _("Your account was not found. Please register again."),
            )
        logger.error(f"HTTP error updating user {telegram_id}: {e}")
        raise ValueError(
            _("Unable to update your profile. Please try again later."),
        )

    except httpx.RequestError as e:
        logger.error(f"Network error updating user {telegram_id}: {e}")
        raise ValueError(_("Network error. Please check your connection."))

    except Exception as e:
        logger.error(f"Unexpected error updating user {telegram_id}: {e}")
        raise ValueError(_("An unexpected error occurred. Please try again."))


async def delete_user(telegram_id: int) -> None:
    """Delete user.

    Args:
        telegram_id: Telegram user ID

    Raises:
        ValueError: If deletion fails

    """
    try:
        http_client = get_http_client_manager()
        await http_client.delete(
            "/v1/users/me",
            telegram_user_id=telegram_id,
        )

        logger.info(f"User {telegram_id} deleted successfully")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            logger.warning(f"Authentication failed for user {telegram_id}")
            raise ValueError(_("Authentication failed. Please try again."))
        if e.response.status_code == 403:
            logger.warning(f"Access forbidden for user {telegram_id}")
            raise ValueError(_("You don't have permission to delete this account."))
        if e.response.status_code == 404:
            logger.info(
                f"User {telegram_id} not found during deletion (already deleted?)",
            )
            # Don't raise error for 404 on deletion - might already be deleted
            return
        logger.error(f"HTTP error deleting user {telegram_id}: {e}")
        raise ValueError(
            _("Unable to delete your account. Please try again later."),
        )

    except httpx.RequestError as e:
        logger.error(f"Network error deleting user {telegram_id}: {e}")
        raise ValueError(_("Network error. Please check your connection."))

    except Exception as e:
        logger.error(f"Unexpected error deleting user {telegram_id}: {e}")
        raise ValueError(_("An unexpected error occurred. Please try again."))
