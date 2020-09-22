from typing import List, Optional
from uuid import UUID

from app import schemas, models, services
from app.api import deps
from app.schemas import Token
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/health", status_code=200)
def get_health() -> str:
    return "healthy!"
