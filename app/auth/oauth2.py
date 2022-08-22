from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.metadata import schema
from  app.database import database
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..metadata.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire_in = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire_in})
    # Below function is used to encode JWT token 
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        # Token is decoded and payload is extracted
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        id: str = payload.get("user")
        role : str = payload.get("role")
        if id is None:
            token_data = schema.TokenData(id = None, role = None)
        else :
            token_data = schema.TokenData(id=id, role=role)
    except JWTError:
        # Error is raised on token expiry or key mismatch
        raise credentials_exception

    return token_data


def get_current_user( session : str= oauth2_scheme, db: Session = Depends(database.get_db) ,):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(session, credentials_exception)
    return token

