import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.api.admin.views import (
    BanAdmin,
    ChatAdmin,
    ChatMemberAdmin,
    FileAdmin,
    MessageAdmin,
    PreferencesAdmin,
    ReactionAdmin,
    ReportAdmin,
    UserAdmin,
    UserMediaAdmin,
)
from app.api.v1.main import router as v1_router
from app.core.config import settings
from app.core.db import engine

app = FastAPI()
app.include_router(v1_router, prefix="/api")

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
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=8000, forwarded_allow_ips="*", proxy_headers=True
    )
