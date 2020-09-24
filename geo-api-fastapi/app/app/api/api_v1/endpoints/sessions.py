from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, services
from app.api import deps
from app.schemas import Token

router = APIRouter()


@router.post("/sessions", status_code=201)
def create_session(
    session_in: schemas.SessionCreate,
    db: Session = Depends(deps.get_db),
) -> schemas.Token:
    token_str = services.session.create_session(session_in.email, session_in.password)
    token = Token(access_token=token_str, token_type="bearer")
    return token
