from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

DEFAULT_GRADE_PARAMETERS = {
    'A+': [91, 100],
    'A': [81, 90],
    'B+': [76, 80],
    'B': [71, 75],
    'C+': [66, 70],
    'C': [61, 65],
    'D': [51, 60],
    'E': [41, 50],
    'F': [1, 40]
}

# Table for main
class MainDB(Base):
    __tablename__ = 'maindb'

    id = Column(String(10), primary_key=True, nullable=False)
    fullname = Column(String(50), nullable=False)
    address = Column(String(500), nullable=True)
    state = Column(String(50), nullable=True)
    pincode = Column(String(10), nullable=True)
    dob = Column(Date, nullable=False)
    email = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=True)
    cls = Column(Integer, nullable=False, server_default='7')
    role = Column(String(10), nullable=False)


class LoginData(Base):
    __tablename__ = 'logininfo'

    id = Column(String(10), primary_key=True, nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(300), nullable=False)
    role = Column(String(10), nullable=False)


class SubjectData(Base):
    __tablename__ = 'subjectdata'

    subjectid = Column(String(10), primary_key=True, nullable=False)
    subjectname = Column(String(50), nullable=False)
    teacherid = Column(String(10), nullable=False)
    isemax = Column(Integer, server_default='20', nullable=False)
    msemax = Column(Integer, server_default='30', nullable=False)
    esemax = Column(Integer, server_default='50', nullable=False)
    totalmax = Column(Integer, server_default='100', nullable=False)
    gradeparam = Column(String(500), server_default=str(DEFAULT_GRADE_PARAMETERS), nullable=False)


class ClassData(Base):
    __tablename__ = 'classdata'

    id = Column(String(10), primary_key=True, nullable=False)
    subjectid = Column(String(10), primary_key=True, nullable=False)
    ise = Column(Integer, server_default='0', nullable=False)
    mse = Column(Integer, server_default='0', nullable=False)
    ese = Column(Integer, server_default='0', nullable=False)
    total = Column(Integer, server_default='0', nullable=False)
    grade = Column(String(2), server_default='F', nullable=False)
