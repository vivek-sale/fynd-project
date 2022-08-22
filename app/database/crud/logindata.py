from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, PendingRollbackError
from app.auth.password_validator import hash
from app.database.crud.userdata import get_student_from_id
from app.database.database import get_db
from app.database import model
from app.metadata import schema

# This file does all database operations on logininfo table

def create_user(user: schema.User, db: Session = Depends(get_db)):
    try:
        new_user = model.LoginData(**user.dict())
        db.add(new_user)
        db.commit()
    except IntegrityError:
        # If the user passed is repeated
        db.rollback()
        return None
    db.refresh(new_user)
    return new_user


# Delete a user from logininfo
def delete_user(id: str, db: Session = Depends(get_db)):
    try:
        if_user = db.query(model.LoginData).filter(model.LoginData == id)
        user = if_user.first()
        if not user:
            return None
        if_user.delete(synchronize_session=False)
        db.commit()
    except IntegrityError:
        # in case of repeating users
        db.rollback()
        return None
    except SQLAlchemyError:
        db.rollback()
        return None
    return id


#  Fetch a userinfo based on username
def get_user(username: str, db: Session = Depends(get_db)):
    try:
        user = db.query(model.LoginData).filter(model.LoginData.id == username).first()
        if not user:
            return None
    except SQLAlchemyError:
        return None
    return user



def add_login_with_id(id: str, db: Session = Depends(get_db)):
    user = get_student_from_id(id=id, db=db)
    new_user = model.LoginData(id=user.id, email=user.email, password=hash(str(user.dob)), role=user.role)
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError or PendingRollbackError:
        db.rollback()
        return None
    db.refresh(new_user)
    return None


# Delete from logininfo
def delete_login(id: str, db: Session = Depends(get_db)):
    try:
        user = db.query(model.LoginData).get(id)
        db.delete(user)
        db.commit()
    except:
        return
    return
