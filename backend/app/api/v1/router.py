from fastapi import APIRouter

from app.api.v1.assistant import router as assistant_router
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.search import router as search_router

router = APIRouter()

router.include_router(assistant_router)
router.include_router(auth_router)
router.include_router(organizations_router)
router.include_router(search_router)
