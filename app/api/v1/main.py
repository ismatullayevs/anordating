from fastapi import APIRouter

from .auth import router as auth_router
from .ban import router as ban_router
from .chat import router as chats_router
from .like import router as likes_router
from .match import router as match_router
from .media import router as media_router
from .place import router as place_router
from .preferences import router as preferences_router
from .reaction import router as reaction_router
from .report import router as report_router
from .user import router as users_router
from .utils import router as utils_router

router = APIRouter(prefix="/v1")
router.include_router(users_router)
router.include_router(chats_router)
router.include_router(utils_router)
router.include_router(preferences_router)
router.include_router(auth_router)
router.include_router(media_router)
router.include_router(ban_router)
router.include_router(place_router)
router.include_router(report_router)
router.include_router(match_router)
router.include_router(likes_router)
router.include_router(reaction_router)
