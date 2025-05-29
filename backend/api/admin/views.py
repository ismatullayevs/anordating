from sqladmin import ModelView

from shared.models.user import User, Preferences, Ban, Reaction
from shared.models.file import UserMedia, File
from shared.models.chat import Chat, ChatMember, Message


class UserAdmin(ModelView, model=User):
    pass


class PreferencesAdmin(ModelView, model=Preferences):
    pass


class BanAdmin(ModelView, model=Ban):
    pass


class ReactionAdmin(ModelView, model=Reaction):
    pass


class UserMediaAdmin(ModelView, model=UserMedia):
    pass


class FileAdmin(ModelView, model=File):
    pass


class ChatAdmin(ModelView, model=Chat):
    pass 


class ChatMemberAdmin(ModelView, model=ChatMember):
    pass


class MessageAdmin(ModelView, model=Message):
    pass
