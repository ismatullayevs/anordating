import uvicorn
from fastapi import FastAPI

from api.routers.users import router as users_router

app = FastAPI()
app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run(app)
