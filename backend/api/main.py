import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.chats import router as chats_router
from api.routers.users import router as users_router
from shared.core.config import settings

app = FastAPI()
app.include_router(users_router)
app.include_router(chats_router)

origins = [
    "http://localhost:5173",
    f"http://{settings.DOMAIN}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
