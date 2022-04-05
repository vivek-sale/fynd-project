from fastapi import APIRouter, Depends, status
from ..database.database import get_db
from ..database import model
from ..database.crud import logindata
from ..metadata import schema
from sqlalchemy.orm import Session
from typing import List
from ..auth.password_validator import hash

router = APIRouter(tags=['user'], include_in_schema=False)


@router.post('/user', status_code=status.HTTP_201_CREATED)
async def usercreate(user: schema.User = Depends(schema.User.as_form), db: Session = Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = logindata.create_user(user=user, db=db)
    if not new_user:
        return {'detail': 'Duplicate userid'}
    return {'detail': 'Created User', 'content': new_user}
    # return new_user
