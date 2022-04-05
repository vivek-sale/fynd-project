from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..metadata import schema
from  ..database import database, model
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..metadata.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire_in = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire_in})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        id: str = payload.get("user")
        role : str = payload.get("role")
        if id is None:
            token_data = schema.TokenData(id = None, role = None)
        else :
            token_data = schema.TokenData(id=id, role=role)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user( session : str= oauth2_scheme, db: Session = Depends(database.get_db) ,):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(session, credentials_exception)
    return token

