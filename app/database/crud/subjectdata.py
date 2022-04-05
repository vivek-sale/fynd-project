from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from . import logindata, classdata
from .. import model
from ...metadata import schema


def get_all_subjects(db: Session = Depends(get_db)):
    subjects = db.query(model.SubjectData).all()
    if not subjects:
        return None
    return subjects


def create_subject(subject: schema.Subject, db: Session = Depends(get_db)):
    try:
        new_subject = model.SubjectData(**subject.dict())
        db.add(new_subject)
        db.commit()
    except IntegrityError:
        return None
    db.refresh(new_subject)
    logindata.add_login_with_id(id=new_subject.teacherid, db=db)
    classdata.add_subject_to_class(subjectid=subject.subjectid, db=db)
    return new_subject


def delete_subject(subjectid: str, db: Session = Depends(get_db)):
    try:
        subjectteach = db.query(model.SubjectData.teacherid).filter(model.SubjectData.subjectid == subjectid).first()
        teacher = db.query(model.SubjectData).filter(model.SubjectData.teacherid == subjectteach.teacherid).all()
        if len(teacher) == 1:
            lgninfo = db.query(model.LoginData).filter(model.LoginData.id == subjectteach.teacherid).first()
            print(lgninfo)
            db.delete(lgninfo)
            db.commit()
        else:
            print('skipped')
        classes = db.query(model.ClassData).filter(model.ClassData.subjectid == subjectid).all()
        for cla in classes:
            db.delete(cla)
        db.commit()
        subject = db.query(model.SubjectData).get(subjectid)
        db.delete(subject)
        db.commit()
    except:
        return False
    return True


def get_all_subject_id(db: Session = Depends(get_db)):
    subjects = db.query(model.SubjectData.subjectid, model.SubjectData.subjectname).all()
    if not subjects:
        return None
    return subjects


def update_subject(subject: schema.Subject, db: Session = Depends(get_db)):
    curr_subject = db.query(model.SubjectData).filter(subject.subjectid == model.SubjectData.subjectid).first()
    curr_subject.subjectname = subject.subjectname
    curr_subject.teacherid = subject.teacherid
    curr_subject.isemax = subject.isemax
    curr_subject.msemax = subject.msemax
    curr_subject.esemax = subject.esemax
    curr_subject.totalmax = subject.isemax + subject.msemax + subject.esemax
    curr_subject.gradeparam = subject.gradeparam
    db.commit()
    return True


def get_subject_for_teacher(teacherid: str, db: Session = Depends(get_db)):
    subjects = db.query(model.SubjectData).filter(model.SubjectData.teacherid == teacherid).all()
    if not subjects:
        return None
    return subjects


def get_subject_from_id(subjectid: str, db: Session = Depends(get_db)):
    subject = db.query(model.SubjectData).filter(model.SubjectData.subjectid == subjectid).first()
    if not subject:
        return None
    return subject
