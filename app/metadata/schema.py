from distutils.command.config import config
from pydantic import BaseModel, EmailStr
from ..utils.form_validator import as_form
from datetime import datetime
from typing import Optional
from .config import DEFAULT_GRADE_PARAMETERS


@as_form
class User(BaseModel):
    id: str
    email: Optional[EmailStr]
    password: str
    role: str


class UserShow(BaseModel):
    id: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None


@as_form
class Subject(BaseModel):
    subjectid: str
    subjectname: str
    teacherid: str
    isemax: Optional[int] = 20
    msemax: Optional[int] = 30
    esemax: Optional[int] = 50
    totalmax: Optional[int] = 100
    gradeparam: Optional[str] = DEFAULT_GRADE_PARAMETERS

    class Config:
        orm_mode = True


@as_form
class AddStud(BaseModel):
    students: str = None

    class Config:
        orm_mode = True
