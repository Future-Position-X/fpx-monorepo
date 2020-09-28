from datetime import timedelta

from app.core.security import create_access_token, verify_password
from app.errors import UnauthorizedError
from app.models import User


def create_session(email: str, password: str) -> str:
    user = User.first_or_fail(email=email)

    try:
        if verify_password(password, user.password):
            token = create_access_token(user.uuid, timedelta(days=14))
            return str(token)
        else:
            raise UnauthorizedError
    except Exception:
        raise UnauthorizedError
