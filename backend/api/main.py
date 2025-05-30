import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.chats import router as chats_router
from api.routers.users import router as users_router
from shared.core.config import settings
from shared.core.db import engine
from sqladmin import Admin
from api.admin.views import UserAdmin, PreferencesAdmin, BanAdmin, ReactionAdmin, UserMediaAdmin, FileAdmin, ChatAdmin, ChatMemberAdmin, MessageAdmin, ReportAdmin

app = FastAPI()
app.include_router(users_router)
app.include_router(chats_router)


admin = Admin(app, engine)

admin.add_view(UserAdmin)
admin.add_view(PreferencesAdmin)
admin.add_view(BanAdmin)
admin.add_view(ReactionAdmin)
admin.add_view(UserMediaAdmin)
admin.add_view(FileAdmin)
admin.add_view(ChatAdmin)
admin.add_view(ChatMemberAdmin)
admin.add_view(MessageAdmin)
admin.add_view(ReportAdmin)

origins = [
    settings.APP_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, forwarded_allow_ips="*", proxy_headers=True)
