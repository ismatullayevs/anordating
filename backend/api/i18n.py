import gettext as gettext
from shared.core.config import settings

locales_dir = settings.BASE_DIR / 'shared/locales'

def get_translator(lang_code='en'):
    translation = gettext.translation('messages', localedir=locales_dir, languages=[lang_code], fallback=True)
    return translation.gettext
