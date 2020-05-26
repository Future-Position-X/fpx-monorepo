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


def get_claims_from_event(event):
    header = event["headers"]["Authorization"]
    parts = header.split(" ")
    token = parts[1]
    claims = jwt.decode(token, os.environ.get("JWT_SECRET"), algorithm='HS256')
    return claims


def get_provider_uuid_from_event(event):
    claims = get_claims_from_event(event)
    return claims["provider_uuid"]