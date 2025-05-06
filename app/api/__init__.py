from fastapi import APIRouter
from . import user, auth, webhook, utils, admin

router = APIRouter()


router.include_router(auth.router, tags=["auth"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
router.include_router(utils.router, prefix="/utils", tags=["utils"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
