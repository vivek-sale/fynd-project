from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.database import get_db
from app.database.crud import logindata, classdata
from app.database import model
from app.metadata import schema


# Get all subject information
def get_all_subjects(db: Session = Depends(get_db)):
    subjects = db.query(model.SubjectData).all()
    if not subjects:
        return None
    return subjects


# Creata a subject in form
def create_subject(subject: schema.Subject, db: Session = Depends(get_db)):
    try:
        new_subject = model.SubjectData(**subject.dict())
        db.add(new_subject)
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(new_subject)
    # Add teacher to logininfo
    logindata.add_login_with_id(id=new_subject.teacherid, db=db)
    # Assign subject to all students in class
    classdata.add_subject_to_class(subjectid=subject.subjectid, db=db)
    return new_subject


# Deleting a subject with its teacher from db and students associated with it
def delete_subject(subjectid: str, db: Session = Depends(get_db)):
    try:
        # Get teacherid from subject
        subjectteach = db.query(model.SubjectData.teacherid).filter(model.SubjectData.subjectid == subjectid).first()
        # get info on teacher as list if len(list) > 1 then skip deleting from logininfo
        teacher = db.query(model.SubjectData).filter(model.SubjectData.teacherid == subjectteach.teacherid).all()
        if len(teacher) == 1:
            try:
                lgninfo = db.query(model.LoginData).filter(model.LoginData.id == subjectteach.teacherid).first()
                db.delete(lgninfo)
                db.commit()
            except:
                print('Already deleted')
        else:
            print('skipped')
        # Delete subject from class for all students
        classes = db.query(model.ClassData).filter(model.ClassData.subjectid == subjectid).all()
        for cla in classes:
            db.delete(cla)
        db.commit()
        subject = db.query(model.SubjectData).get(subjectid)
        db.delete(subject)
        db.commit()
    except Exception as e:
        return False
    return True


# Get all subject id and subject names
def get_all_subject_id(db: Session = Depends(get_db)):
    subjects = db.query(model.SubjectData.subjectid, model.SubjectData.subjectname).all()
    if not subjects:
        return None
    return subjects


# Update infotrmation for a subject
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

# Get subject with the help of teacherid
def get_subject_for_teacher(teacherid: str, db: Session = Depends(get_db)):
    subjects = db.query(model.SubjectData).filter(model.SubjectData.teacherid == teacherid).all()
    if not subjects:
        return None
    return subjects


# Get subject based on subject
def get_subject_from_id(subjectid: str, db: Session = Depends(get_db)):
    subject = db.query(model.SubjectData).filter(model.SubjectData.subjectid == subjectid).first()
    if not subject:
        return None
    return subject
