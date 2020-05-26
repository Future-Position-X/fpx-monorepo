import jwt
import os
from datetime import datetime, timedelta
import bcrypt

def authenticate(user, password):
    return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf8"))


def create_access_token(user_uuid, provider_uuid):
    claims = {
        "sub": user_uuid,
        "exp": datetime.utcnow() + timedelta(days=14),
        "provider_uuid": provider_uuid
    }

    token = jwt.encode(claims, os.environ.get("JWT_SECRET"), algorithm='HS256')
    return token.decode("utf-8")