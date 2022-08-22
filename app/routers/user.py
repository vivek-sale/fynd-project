from fastapi import APIRouter, Depends, status
from app.database.database import get_db
from app.database import model
from app.database.crud import logindata
from app.metadata import schema
from sqlalchemy.orm import Session
from app.auth.password_validator import hash
# this route will not be shown in openapi docs

router = APIRouter(tags=['user'], include_in_schema=False)


# this was used to configure logininfo 
@router.post('/user', status_code=status.HTTP_201_CREATED, description='Route for adding a user to logindb')
async def usercreate(user: schema.User = Depends(schema.User.as_form), db: Session = Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = logindata.create_user(user=user, db=db)
    if not new_user:
        return {'detail': 'Duplicate userid'}
    return {'detail': 'Created User', 'content': new_user}
