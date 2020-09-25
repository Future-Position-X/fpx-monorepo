from fastapi import APIRouter

router = APIRouter()


@router.get("/health", status_code=200)
def get_health() -> str:
    return "healthy!"
