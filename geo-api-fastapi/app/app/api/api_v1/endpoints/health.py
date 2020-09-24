from fastapi import APIRouter

router = APIRouter()


@router.post("/health", status_code=200)
def get_health() -> str:
    return "healthy!"
