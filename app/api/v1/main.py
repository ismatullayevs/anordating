from fastapi import APIRouter

from .chats import router as chats_router
from .users import router as users_router
from .utils import router as utils_router

router = APIRouter(prefix="/v1")
router.include_router(users_router)
router.include_router(chats_router)
router.include_router(utils_router)
