from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.crud.userdata import get_all_students_from_class
from app.database.database import get_db
from app.database.crud import subjectdata
from app.database.crud.logindata import add_login_with_id, delete_login
from app.database import model
from app.metadata import schema
from app.utils.marks_validator import marks_validator



# This file contains all the database operations on classdata table

def extract(studentlst: list, db: Session = Depends(get_db)):
    if not studentlst:
        return None
    # Returns all the subjects from subjectdata table
    subjects = subjectdata.get_all_subjects(db=db)
    if not subjects:
        return None
    
    # Dictionary to store all the update cases
    errors: dict = {'success': [], 'repeat': [], 'invalid': []}
    for student in studentlst:
        # Check if student is valid
        flag = check_student_main(id=student, db=db)
        if flag == False:
            errors['invalid'].append(student)
            continue
        # Check if student is already present for subject
        for subject in subjects:
            flag2 = check_student(id=student, subjectid=subject.subjectid, db=db)
            if not flag2:
                errors['repeat'].append(student)
            else:
                errors['success'].append(student)
    # remove duplicates in success and repeat
    errors = {'success': list(set(errors['success'])), 'repeat': list(set(errors['repeat'])),
              'invalid': errors['invalid']}
    
    # Add all the students to classdata who are in success
    for success in errors['success']:
        add_login_with_id(id=success, db=db)
    return errors



# Add student for subject
def add_student(id: str, subjectid: str, db: Session = Depends(get_db)):
    student = {'id': id, 'subjectid': subjectid}
    new_stud_sub = model.ClassData(**student)
    db.add(new_stud_sub)
    db.commit()
    return False


# Check if student is present in maindb
def check_student_main(id: str, db: Session = Depends(get_db)):
    stud = db.query(model.MainDB).filter(model.MainDB.id == id).first()
    if not stud:
        return False
    return True



# Check if student is present for given id and subject
def check_student(id: str, subjectid: str, db: Session = Depends(get_db)):
    stud = db.query(model.ClassData).filter(model.ClassData.id == id).filter(
        model.ClassData.subjectid == subjectid).first()
    if not stud:
        add_student(id=id, subjectid=subjectid, db=db)
        return True
    return False


# Get all data from classdata
def get_all_marks(db: Session = Depends(get_db)):
    entity = db.query(model.ClassData).all()
    if not entity:
        return None
    else:
        return entity



# Delete a student from class
def delete_student(id: str, db: Session = Depends(get_db)):
    students = db.query(model.ClassData).filter(model.ClassData.id == id).all()
    if not students:
        return False
    # Delete student from logindata
    delete_login(id=id, db=db)
    try:
        for student in students:
            db.delete(student)
        db.commit()
    except:
        # On failure rollback
        db.rollback()
        return False
    return True



# Get marks for all subjects of a student
def get_all_marks_student(id: str, db: Session = Depends(get_db)):
    entity = db.query(model.ClassData).filter(model.ClassData.id == id).all()
    if not entity:
        return None
    else:
        return entity


# Add subject to the class and assign it to all students
def add_subject_to_class(subjectid: str, db: Session = Depends(get_db)):
    students = get_all_students_from_class(db=db)
    for student in students:
        add_student(id=student.id, subjectid=subjectid, db=db)
    return



# Get marks for a subject of all students
def get_all_marks_subject(subjectid: str, db: Session = Depends(get_db)):
    students = db.query(model.ClassData).filter(model.ClassData.subjectid == subjectid).all()
    if not students:
        return None
    else:
        return students



# Get marks of a subject for specific subject
def get_marks_for_student_of_subject(studentid: str, subjectid: str, db: Session = Depends(get_db)):
    marks = db.query(model.ClassData).filter(model.ClassData.id == studentid).filter(
        model.ClassData.subjectid == subjectid).first()
    if not marks:
        return None
    else:
        return marks



# Update marks of a given student subject combo
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



# Bulkuploading marks 
def bulkupload_marks(marklist: list, subjectid: str, db: Session = Depends(get_db)):
    summary = {
        'succeeded': [],
        'mismatch': [],
        'invalid': []
    }

    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    for marks in marklist:
        marks = marks.split(',')
        # Check marks constraints
        if int(marks[1]) > subject.isemax or int(marks[2]) > subject.msemax or int(marks[3]) > subject.esemax:
            summary['mismatch'].append(marks[0])
        else:
            succ = update_marks(studentid=marks[0], subjectid=subjectid, ise=int(marks[1]), mse=int(marks[2]),
                                ese=int(marks[3]), db=db)
            if succ == False:
                # If student is not found
                summary['invalid'].append(marks[0])
            else:
                summary['succeeded'].append(marks[0])
    return summary
