from aiogram.utils.i18n import I18n, FSMI18nMiddleware
from shared.core.config import settings


i18n = I18n(
    path=settings.BASE_DIR / "shared" / "locales",
    default_locale="en",
    domain="messages",
)
i18n_middleware = FSMI18nMiddleware(i18n)
