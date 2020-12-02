from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from app import models, schemas, services
from app.core import security
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.base_model import BaseModel

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token", auto_error=False
)


def get_db() -> None:
    try:
        session = AsyncSessionLocal
        with session.no_autoflush as s:
            BaseModel.set_session(s)
    except Exception as e:
        print(e)
        raise e


def get_current_user(token: str = Depends(reusable_oauth2)) -> Optional[schemas.User]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError, AttributeError) as e:
        if type(e) != AttributeError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        else:
            return None
    assert token_data.sub is not None
    user = services.user.get_user(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.User.from_dto(user)


def get_current_user_or_guest(
    current_user: Optional[models.User] = Depends(get_current_user),
) -> Optional[models.User]:
    if current_user:
        return current_user
    else:
        return models.User(
            uuid="00000000-0000-0000-0000-000000000000",
            provider_uuid="00000000-0000-0000-0000-000000000000",
        )
