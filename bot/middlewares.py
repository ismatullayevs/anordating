from aiogram.utils.i18n import FSMI18nMiddleware, I18n

from app.core.config import settings

# TODO: Create separate settings for bot

i18n = I18n(
    path=settings.BASE_DIR / "bot" / "locales",
    default_locale="en",
    domain="messages",
)
i18n_middleware = FSMI18nMiddleware(i18n)
