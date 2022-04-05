from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.crud.userdata import get_all_students_from_class
from ..database import get_db
from . import subjectdata
from .logindata import add_login_with_id, delete_login
from .. import model
from ...metadata import schema
from ...utils.marks_validator import marks_validator

errors: dict = {'success': [], 'repeat': [], 'invalid': []}


def extract(studentlst: list, db: Session = Depends(get_db)):
    if not studentlst:
        return None
    subjects = subjectdata.get_all_subjects(db=db)
    if not subjects:
        return None
    errors: dict = {'success': [], 'repeat': [], 'invalid': []}
    for student in studentlst:
        flag = check_student_main(id=student, db=db)
        if flag == False:
            errors['invalid'].append(student)
            continue
        for subject in subjects:
            flag2 = check_student(id=student, subjectid=subject.subjectid, db=db)
            if not flag2:
                errors['repeat'].append(student)
            else:
                errors['success'].append(student)
    errors = {'success': list(set(errors['success'])), 'repeat': list(set(errors['repeat'])),
              'invalid': errors['invalid']}
    for success in errors['success']:
        add_login_with_id(id=success, db=db)
    return errors


def add_student(id: str, subjectid: str, db: Session = Depends(get_db)):
    student = {'id': id, 'subjectid': subjectid}
    new_stud_sub = model.ClassData(**student)
    db.add(new_stud_sub)
    db.commit()
    return False


def check_student_main(id: str, db: Session = Depends(get_db)):
    stud = db.query(model.MainDB).filter(model.MainDB.id == id).first()
    if not stud:
        return False
    return True


def check_student(id: str, subjectid: str, db: Session = Depends(get_db)):
    stud = db.query(model.ClassData).filter(model.ClassData.id == id).filter(
        model.ClassData.subjectid == subjectid).first()
    if not stud:
        add_student(id=id, subjectid=subjectid, db=db)
        return True
    return False


def get_all_marks(db: Session = Depends(get_db)):
    entity = db.query(model.ClassData).all()
    if not entity:
        return None
    else:
        return entity


def delete_student(id: str, db: Session = Depends(get_db)):
    students = db.query(model.ClassData).filter(model.ClassData.id == id).all()
    if not students:
        return False
    delete_login(id=id, db=db)
    try:
        for student in students:
            db.delete(student)
            db.commit()
    except:
        return False
    return True


def get_all_marks_student(id: str, db: Session = Depends(get_db)):
    entity = db.query(model.ClassData).filter(model.ClassData.id == id).all()
    if not entity:
        return None
    else:
        return entity


def add_subject_to_class(subjectid: str, db: Session = Depends(get_db)):
    students = get_all_students_from_class(db=db)
    for student in students:
        add_student(id=student.id, subjectid=subjectid, db=db)
    return


def get_all_marks_subject(subjectid: str, db: Session = Depends(get_db)):
    students = db.query(model.ClassData).filter(model.ClassData.subjectid == subjectid).all()
    if not students:
        return None
    else:
        return students


def get_marks_for_student_of_subject(studentid: str, subjectid: str, db: Session = Depends(get_db)):
    marks = db.query(model.ClassData).filter(model.ClassData.id == studentid).filter(
        model.ClassData.subjectid == subjectid).first()
    if not marks:
        return None
    else:
        return marks


def update_marks(studentid: str, subjectid: str, ise: int, mse: int, ese: int, db: Session = Depends(get_db)):
    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    marks = get_marks_for_student_of_subject(studentid=studentid, subjectid=subjectid, db=db)
    if not marks:
        return False
    marks.ise = ise
    marks.mse = mse
    marks.ese = ese
    marks.total = ise + mse + ese
    marks.grade = marks_validator(total=marks.total, param=subject.gradeparam)
    db.commit()
    return True


def bulkupload_marks(marklist: list, subjectid: str, db: Session = Depends(get_db)):
    summary = {
        'succeeded': [],
        'mismatch': [],
        'invalid': []
    }
    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    for marks in marklist:
        marks = marks.split(',')
        if int(marks[1]) > subject.isemax or int(marks[2]) > subject.msemax or int(marks[3]) > subject.esemax:
            summary['mismatch'].append(marks[0])
        else:
            succ = update_marks(studentid=marks[0], subjectid=subjectid, ise=int(marks[1]), mse=int(marks[2]),
                                ese=int(marks[3]), db=db)
            if succ == False:
                summary['invalid'].append(marks[0])
            else:
                summary['succeeded'].append(marks[0])
    return summary
