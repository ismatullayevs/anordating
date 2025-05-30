from sqladmin import ModelView

from shared.models.user import Report, User, Preferences, Ban, Reaction
from shared.models.file import UserMedia, File
from shared.models.chat import Chat, ChatMember, Message


class UserAdmin(ModelView, model=User):
    column_list = [
        User.telegram_id, User.name, User.rating, User.gender, User.is_active, User.created_at
    ]
    column_searchable_list = [User.name, User.telegram_id, User.bio]
    column_sortable_list = [User.birth_date, User.rating, User.created_at, User.is_active, User.gender]
    can_edit = False
    can_create = False
    can_delete = False


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


class ReportAdmin(ModelView, model=Report):
    pass