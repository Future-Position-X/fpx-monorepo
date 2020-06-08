import jwt
from datetime import datetime, timedelta
import bcrypt
from flask import current_app

def authenticate(user, password):
    return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf8"))


def create_access_token(user_uuid, provider_uuid):
    claims = {
        "sub": str(user_uuid),
        "exp": datetime.utcnow() + timedelta(days=14),
        "provider_uuid": str(provider_uuid)
    }

    token = jwt.encode(claims, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token.decode("utf-8")