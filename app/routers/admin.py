from fastapi import APIRouter, UploadFile, status, Depends, Form, Request, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..database.database import get_db
from ..auth.oauth2 import get_current_user
from ..database import model
from ..metadata import schema
from ..database.crud import subjectdata, userdata, classdata
from sqlalchemy.orm import Session
from ..bg_tasks.sendteachmail import send_mail_to_teacher

router = APIRouter(tags=['Admin'])

templates = Jinja2Templates(directory="templates")

# For rendering admin homepage template
@router.get('/admin/home', status_code=status.HTTP_200_OK)           
async def fetch_subjects(request: Request, db: Session = Depends(get_db)):

    token_data = None
    try:
        # Token is checked from cookie and data stored in it like userid and role
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        print(e)
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    subjects = subjectdata.get_all_subjects(db=db)
    teachers = userdata.get_all_teachers(db=db)
    return templates.TemplateResponse('protected/admin/adminhome.html',
                                      {"request": request, 'data': subjects, 'teachers': teachers}, )


@router.post('/admin/home', status_code=status.HTTP_201_CREATED)
async def load_subjects(request: Request, backgroundtask: BackgroundTasks,
                        subject: schema.Subject = Depends(schema.Subject.as_form), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    new_subject = subjectdata.create_subject(subject=subject, db=db)
    if not new_subject:
        response = RedirectResponse('/admin/home', status_code=304,
                                    headers={'message': 'Subject of this ID is already Present'})
        return response
    teacherinfo = db.query(model.MainDB.fullname, model.MainDB.email).filter(
        new_subject.teacherid == model.MainDB.id).first()
    send_mail_to_teacher(backgroundtask=backgroundtask, emailid=teacherinfo.email, name=teacherinfo.fullname,
                         subject=new_subject.subjectname)
    response = RedirectResponse('/admin/home', status_code=302,
                                headers={'message': f'New subject {new_subject.subjectname} is added'})
    return response


@router.delete('/admin/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(request: Request, id: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    is_succeeded = subjectdata.delete_subject(subjectid=id, db=db)
    if not is_succeeded:
        return {'Message': 'Failed to delete'}
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "subject": None
    })


@router.get('/admin/update/{id}', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def fetch_subjects(id: str, request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    subject = db.query(model.SubjectData).filter(model.SubjectData.subjectid == id).first()
    teachers = db.query(model.MainDB).filter(model.MainDB.role == 'TEACHER').all()
    return templates.TemplateResponse('protected/admin/adminupdate.html',
                                      {"request": request, 'data': subject, 'teachers': teachers})


@router.post('/admin/update/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_subject(request: Request, id: str, subject: schema.Subject = Depends(schema.Subject.as_form),
                         db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    is_succeded = subjectdata.update_subject(subject=subject, db=db)
    if is_succeded == False:
        return RedirectResponse(f'/admin/update/{id}', status_code=303)
    return RedirectResponse('/admin/home', status_code=303)


@router.get('/admin/students', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def load_students(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    students = userdata.get_all_students_from_class(db=db)
    classdt = classdata.get_all_marks(db=db)
    subjectnames = subjectdata.get_all_subject_id(db=db)
    return templates.TemplateResponse('protected/admin/adminstudent.html',
                                      {'request': request, 'students': students, 'classdata': classdt,
                                       'subjects': subjectnames})


@router.post('/admin/loadstudent', status_code=status.HTTP_201_CREATED)
async def add_students(request: Request, students: str = Form(...), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    if not students:
        return RedirectResponse('/admin/students', {'message': 'No new students added'})
    studlist = students.split(',')
    summary = classdata.extract(studentlst=studlist, db=db)
    return templates.TemplateResponse('/protected/admin/adminloadstud.html', {'request': request, 'summary': summary})


@router.get('/admin/student/get_template', status_code=status.HTTP_302_FOUND)
async def get_template(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    return FileResponse(r'C:\Users\Vivek\Desktop\Fastapp\resources\template_student.csv', media_type='text/csv',
                        filename='template_student.csv')


@router.post('/admin/bulkloadstudent', status_code=status.HTTP_201_CREATED)
async def bulk_load(request: Request, bulkfile: UploadFile = File(...), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    bulk_list = await bulkfile.read()
    bulk_list = bulk_list.decode()
    studlist = bulk_list.split()
    studlist.pop(0)
    summary = classdata.extract(studentlst=studlist, db=db)
    return templates.TemplateResponse('/protected/admin/adminloadstud.html', {'request': request, 'summary': summary})


@router.delete('/admin/student/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(request: Request, id: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'ADMIN':
        return RedirectResponse('/404', status_code=303)
    is_succeeded = classdata.delete_student(id=id, db=db)
    if not is_succeeded:
        return {'Message': 'Failed to delete'}
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "subject": None
    })
