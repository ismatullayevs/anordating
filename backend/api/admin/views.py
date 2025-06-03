from sqladmin import ModelView

from shared.models.chat import Chat, ChatMember, Message
from shared.models.file import File, UserMedia
from shared.models.user import Ban, Preferences, Reaction, Report, User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.telegram_id,
        User.name,
        User.rating,
        User.gender,
        User.is_active,
        User.created_at,
    ]
    column_searchable_list = [User.name, User.telegram_id, User.bio]
    column_sortable_list = [
        User.birth_date,
        User.rating,
        User.created_at,
        User.is_active,
        User.gender,
    ]
    can_edit = False
    can_create = False
    can_delete = False
    column_default_sort = [(User.created_at, True)]


class PreferencesAdmin(ModelView, model=Preferences):
    pass


class BanAdmin(ModelView, model=Ban):
    column_list = [
        Ban.user_telegram_id,
        Ban.reason,
        Ban.created_at,
        Ban.expires_at,
    ]
    column_searchable_list = [Ban.user_telegram_id, Ban.reason]
    column_sortable_list = [Ban.created_at, Ban.expires_at]
    column_default_sort = [(Ban.created_at, True)]


class ReactionAdmin(ModelView, model=Reaction):
    column_list = [
        Reaction.from_user_id,
        Reaction.to_user_id,
        Reaction.reaction_type,
        Reaction.created_at,
    ]
    column_searchable_list = [Reaction.from_user_id, Reaction.to_user_id]
    column_sortable_list = [Reaction.created_at, Reaction.reaction_type]
    can_edit = False
    can_create = False
    can_delete = False
    column_default_sort = [(Reaction.created_at, True)]


class UserMediaAdmin(ModelView, model=UserMedia):
    can_edit = False
    can_create = False
    can_delete = False


class FileAdmin(ModelView, model=File):
    pass


class ChatAdmin(ModelView, model=Chat):
    pass


class ChatMemberAdmin(ModelView, model=ChatMember):
    pass


class MessageAdmin(ModelView, model=Message):
    column_list = [
        Message.chat_id,
        Message.user_id,
        Message.text,
        Message.created_at,
    ]
    column_searchable_list = [Message.text, Message.user_id, Message.chat_id]
    column_sortable_list = [Message.created_at]
    can_edit = False
    can_create = False
    can_delete = False
    column_default_sort = [(Message.created_at, True)]


class ReportAdmin(ModelView, model=Report):
    column_list = [
        Report.from_user_id,
        Report.to_user_id,
        Report.reason,
        Report.created_at,
    ]
    column_searchable_list = [Report.from_user_id, Report.to_user_id, Report.reason]
    column_sortable_list = [Report.created_at]
    column_default_sort = [(Report.created_at, True)]
