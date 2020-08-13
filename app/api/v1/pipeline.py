from fastapi import APIRouter

from app.workflow import flow

router = APIRouter()


@router.get("/")
def post_pipeline():
    flow.run()
