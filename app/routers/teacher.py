from urllib import response
from fastapi import APIRouter, UploadFile, status, Depends, Form, Request, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.utils.marks_validator import marks_validator
from ..database.database import get_db
from ..auth.oauth2 import get_current_user
from ..database import model
from ..metadata import schema
from ..database.crud import subjectdata, userdata, classdata
from sqlalchemy.orm import Session

router = APIRouter(tags=['Teacher'])

templates = Jinja2Templates(directory="templates")


@router.get('/teacher', status_code=status.HTTP_202_ACCEPTED)
async def load_subjects(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=303)

    subjects = subjectdata.get_subject_for_teacher(teacherid=token_data.id, db=db)
    teacher = userdata.get_student_from_id(id=token_data.id, db=db)
    return templates.TemplateResponse('protected/teacher/teacherhome.html',
                                      {'request': request, 'teacher': teacher, 'subjects': subjects})


@router.get('/teacher/{subjectid}', status_code=status.HTTP_202_ACCEPTED)
async def show_students(request: Request, subjectid: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=303)

    students = classdata.get_all_marks_subject(subjectid=subjectid, db=db)
    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    teacher = userdata.get_student_from_id(id=token_data.id, db=db)
    # return {'students':students, 'subject': subject}
    return templates.TemplateResponse('protected/teacher/teacherstudent.html',
                                      {'request': request, 'students': students, 'subject': subject,
                                       'teacher': teacher})


@router.get('/teacher/{studentid}/{subjectid}', status_code=202)
async def load_marks(request: Request, subjectid: str, studentid: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=303)

    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    marks = classdata.get_marks_for_student_of_subject(studentid=studentid, subjectid=subjectid, db=db)
    return templates.TemplateResponse('protected/teacher/teacherupdate.html',
                                      {'request': request, 'subject': subject, 'marks': marks})


@router.post('/teacher/{studentid}/{subjectid}', status_code=202)
async def update_marks(request: Request, subjectid: str, studentid: str, ise: int = Form(...), mse: int = Form(...),
                       ese: int = Form(...), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=303)

    is_succeeded = classdata.update_marks(studentid=studentid, subjectid=subjectid, ise=ise, mse=mse, ese=ese, db=db)
    if is_succeeded == True:
        return RedirectResponse(f'/teacher/{subjectid}', status_code=303)
    return None


@router.get('/download_mark_template', status_code=302)
async def download_template(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=303)

    return FileResponse(r'C:\Users\Vivek\Desktop\Fastapp\resources\template_marks.csv', media_type='text/csv',
                        filename='template_marks.csv')


@router.post('/bulkmarks/{subjectid}', status_code=status.HTTP_201_CREATED)
async def bulk_load_marks(request: Request, subjectid: str, bulkfile: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=303)

    bulk_list = await bulkfile.read()
    bulk_list = bulk_list.decode()
    marklist = bulk_list.split()
    marklist = marklist[5:]
    summary = classdata.bulkupload_marks(marklist=marklist, subjectid=subjectid, db=db)
    return templates.TemplateResponse('protected/teacher/teacherloadsummary.html',
                                      {'request': request, 'summary': summary})
