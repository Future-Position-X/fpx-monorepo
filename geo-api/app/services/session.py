from datetime import datetime, timedelta

import bcrypt
import jwt
from flask import current_app

from app.models import User


def authenticate(user, password):
    return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf8"))


def create_access_token(user_uuid, provider_uuid):
    claims = {
        "sub": str(user_uuid),
        "exp": datetime.utcnow() + timedelta(days=14),
        "provider_uuid": str(provider_uuid),
    }

    token = jwt.encode(claims, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token.decode("utf-8")


def create_session(email: str, password: str) -> str:
    user = User.first_or_fail(email=email)

    try:
        if authenticate(user, password):
            token = create_access_token(user.uuid, user.provider_uuid)
            return str(token)
        else:
            raise ValueError
    except Exception:
        raise ValueError
