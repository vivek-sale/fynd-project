from fastapi import Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import model


def get_all_teachers(db: Session = Depends(get_db)):
    teachers = db.query(model.MainDB.id, model.MainDB.fullname).filter(model.MainDB.role == 'TEACHER').all()
    if not teachers:
        return None
    return teachers


def get_all_students(db: Session = Depends(get_db)):
    students = db.query(model.MainDB.id, model.MainDB.fullname).filter(model.MainDB.role == 'STUDENT').all()
    if not students:
        return None
    return students


def get_student_from_id(id: str, db: Session = Depends(get_db)):
    user = db.query(model.MainDB).filter(model.MainDB.id == id).first()
    if not user:
        return None
    return user


def get_all_students_from_class(db: Session = Depends(get_db)):
    stud = db.query(model.ClassData.id).distinct(model.ClassData.id).group_by(model.ClassData.id).all()
    student = []
    for stu in stud:
        studen = db.query(model.MainDB.id, model.MainDB.fullname).filter(model.MainDB.id == stu.id).first()
        student.append(studen)
    return student
