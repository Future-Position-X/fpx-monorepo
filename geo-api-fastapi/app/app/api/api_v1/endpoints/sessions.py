from typing import List, Optional
from uuid import UUID

from app import schemas, models, services
from app.api import deps
from app.schemas import Token
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/sessions", status_code=201)
def create_session(
    session_in: schemas.SessionCreate,
    db: Session = Depends(deps.get_db),
) -> schemas.Token:
    token_str = services.session.create_session(session_in.email, session_in.password)
    token = Token(access_token=token_str, token_type="bearer")
    return token
