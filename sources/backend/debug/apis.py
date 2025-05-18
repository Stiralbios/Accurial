import sys

from fastapi import APIRouter

router = APIRouter(prefix="/api/debug/healthcheck", tags=["debug", "healthcheck"])


@router.get("/status")
async def get_status():
    return {
        "status": "ok",
        "stack": {
            "python": sys.version,
        },
    }
