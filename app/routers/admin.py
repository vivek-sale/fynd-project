from fastapi import APIRouter, UploadFile, status, Depends, Form, Request, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.database.database import get_db
from app.auth.oauth2 import get_current_user
from app.database import model
from app.metadata import schema
from app.database.crud import subjectdata, userdata, classdata
from sqlalchemy.orm import Session
from app.bg_tasks.sendteachmail import send_mail_to_teacher
from app.metadata.config import settings

router = APIRouter(tags=['Admin'])

templates = Jinja2Templates(directory="templates")

# For rendering admin homepage template
@router.get('/admin/home', status_code=status.HTTP_200_OK, description='Main page for class teacher which has functionality to add/delete subjects/students')           
async def fetch_subjects(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        # Token is checked from cookie and data stored in it like userid and role is fetched into token_data
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        # Errors like cookie expiration, token expiry caught here
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        # Role specific route if another user comes here caught and sent to 404
        return RedirectResponse('/404', status_code=301)
    subjects = subjectdata.get_all_subjects(db=db)
    teachers = userdata.get_all_teachers(db=db)
    return templates.TemplateResponse('protected/admin/adminhome.html',
                                      {"request": request, 'data': subjects, 'teachers': teachers}, )


# Route to add new subject
@router.post('/admin/home', status_code=status.HTTP_201_CREATED, description='Adding a new subject in class, along with assigning teacher and grades')
async def load_subjects(request: Request, backgroundtask: BackgroundTasks,
                        subject: schema.Subject = Depends(schema.Subject.as_form), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    new_subject = subjectdata.create_subject(subject=subject, db=db)
    if not new_subject:
        # Already present subjectname
        response = RedirectResponse('/admin/home', status_code=304,
                                    headers={'message': 'Subject of this ID is already Present'})
        return response
    # Getting teacherinfo
    teacherinfo = db.query(model.MainDB.fullname, model.MainDB.email).filter(
        new_subject.teacherid == model.MainDB.id).first()
    # Sending a mail to teachr who have been assigned the subject
    send_mail_to_teacher(backgroundtask=backgroundtask, emailid=teacherinfo.email, name=teacherinfo.fullname,
                         subject=new_subject.subjectname)
    response = RedirectResponse('/admin/home', status_code=302,
                                headers={'message': f'New subject {new_subject.subjectname} is added'})
    return response


# Deleting a subject
@router.delete('/admin/delete/{id}', status_code=status.HTTP_204_NO_CONTENT, description='A subject is deleted from here based on subjectid, it is also removed from other databases present')
async def delete_subject(request: Request, id: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    is_succeeded = subjectdata.delete_subject(subjectid=id, db=db)
    if not is_succeeded:
        return {'Message': 'Failed to delete'}
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "subject": None
    })

# Loading page to update a subject information
@router.get('/admin/update/{id}', status_code=status.HTTP_200_OK, response_class=HTMLResponse, description='Update method to update subject information except subject id as it is fixed.')
async def fetch_subjects(id: str, request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    subject = db.query(model.SubjectData).filter(model.SubjectData.subjectid == id).first()
    teachers = db.query(model.MainDB).filter(model.MainDB.role == 'TEACHER').all()
    return templates.TemplateResponse('protected/admin/adminupdate.html',
                                      {"request": request, 'data': subject, 'teachers': teachers})


# Method to do the updating of subject
@router.post('/admin/update/{id}', status_code=status.HTTP_202_ACCEPTED, description='Contains actual logic for updating the subject.')
async def update_subject(request: Request, id: str, subject: schema.Subject = Depends(schema.Subject.as_form),
                         db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    is_succeded = subjectdata.update_subject(subject=subject, db=db)
    if is_succeded == False:
        return RedirectResponse(f'/admin/update/{id}', status_code=303)
    return RedirectResponse('/admin/home', status_code=303)


# Method to load the students page
@router.get('/admin/student', status_code=status.HTTP_200_OK, description='This route fetches the data required to display students like userdata pf student, subjects and marks and displays it in tabular format on front end.')
async def load_students(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    students = userdata.get_all_students_from_class(db=db)
    classdt = classdata.get_all_marks(db=db)
    subjectnames = subjectdata.get_all_subject_id(db=db)
    return templates.TemplateResponse('protected/admin/adminstudent.html',
                                      {'request': request, 'students': students, 'classdata': classdt,
                                       'subjects': subjectnames})


# Add new students
@router.post('/admin/loadstudent', status_code=status.HTTP_201_CREATED, description='Add multiple or single student at the same time redirects to a summary page to review.')
async def add_students(request: Request, students: str = Form(...), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    if not students:
        return RedirectResponse('/admin/students', {'message': 'No new students added'})
    # Multiple students can be added at the same time with comma separation
    studlist = students.split(',')
    studlist = [stud.upper() for stud in studlist]
    summary = classdata.extract(studentlst=studlist, db=db)
    return templates.TemplateResponse('/protected/admin/adminloadstud.html', {'request': request, 'summary': summary})


# To download a template
@router.get('/admin/student/get_template', status_code=status.HTTP_302_FOUND, description='Used to download a teplate for adding student id')
async def get_template(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    return FileResponse(settings.student_template_path, media_type='text/csv',
                        filename='template_student.csv')


# Upload a file
@router.post('/admin/bulkloadstudent', status_code=status.HTTP_201_CREATED, description='Accepts a file from user in given format and does calculations on it in background for marks. Also provides summary at the end.')
async def bulk_load(request: Request, bulkfile: UploadFile = File(...), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    bulk_list = await bulkfile.read()
    bulk_list = bulk_list.decode()
    studlist = bulk_list.split()
    studlist.pop(0)
    studlist = [stud.upper() for stud in studlist]
    summary = classdata.extract(studentlst=studlist, db=db)
    return templates.TemplateResponse('/protected/admin/adminloadstud.html', {'request': request, 'summary': summary})


# Used to delete student information from class
@router.delete('/admin/student/delete/{id}', status_code=status.HTTP_204_NO_CONTENT, description='Student is deleted from classdata as well as logininfo database.')
async def delete_student(request: Request, id: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=301)
    is_succeeded = classdata.delete_student(id=id, db=db)
    if not is_succeeded:
        return {'Message': 'Failed to delete'}
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "subject": None
    })
