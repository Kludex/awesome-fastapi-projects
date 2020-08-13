from fastapi import APIRouter

from app.api.v1.pipeline import router as pipeline
from app.api.v1.repositories import router as repositories

router = APIRouter()

router.include_router(pipeline, prefix="/pipeline", tags=["Pipeline"])
router.include_router(repositories, prefix="/repositories", tags=["Repositories"])
