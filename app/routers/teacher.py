from fastapi import APIRouter, UploadFile, status, Depends, Form, Request, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.database.database import get_db
from app.auth.oauth2 import get_current_user
from app.database.crud import subjectdata, userdata, classdata
from sqlalchemy.orm import Session
from app.metadata.config import settings

router = APIRouter(tags=['Teacher'])

templates = Jinja2Templates(directory="templates")

# Rendering teacherhome route
@router.get('/teacher', status_code=status.HTTP_202_ACCEPTED, description='Rendering homepage for teacher to choose all subjects he has been assigned for the class.')
async def load_subjects(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=301)
    # Validate teacher
    subjects = subjectdata.get_subject_for_teacher(teacherid=token_data.id, db=db)
    teacher = userdata.get_student_from_id(id=token_data.id, db=db)
    return templates.TemplateResponse('protected/teacher/teacherhome.html',
                                      {'request': request, 'teacher': teacher, 'subjects': subjects})



# Go to specific subject of a teacher
@router.get('/teacher/{subjectid}', status_code=status.HTTP_202_ACCEPTED, description='Getting page for teacher which has marks of subject oa all students.')
async def show_students(request: Request, subjectid: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=301)

    students = classdata.get_all_marks_subject(subjectid=subjectid, db=db)
    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    teacher = userdata.get_student_from_id(id=token_data.id, db=db)
    return templates.TemplateResponse('protected/teacher/teacherstudent.html',
                                      {'request': request, 'students': students, 'subject': subject,
                                       'teacher': teacher})



# Getting page for editing marks of a subject of teacher
@router.get('/teacher/{studentid}/{subjectid}', status_code=202, description='Contains form for editing marks with given constraints.')
async def load_marks(request: Request, subjectid: str, studentid: str, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=301)

    subject = subjectdata.get_subject_from_id(subjectid=subjectid, db=db)
    # Got subject information for max parameters
    marks = classdata.get_marks_for_student_of_subject(studentid=studentid, subjectid=subjectid, db=db)
    return templates.TemplateResponse('protected/teacher/teacherupdate.html',
                                      {'request': request, 'subject': subject, 'marks': marks})



# Post response for updating marks
@router.post('/teacher/{studentid}/{subjectid}', status_code=202, description='Route for updating marks. Parameters get checked at front end for validation.')
async def update_marks(request: Request, subjectid: str, studentid: str, ise: int = Form(...), mse: int = Form(...),
                       ese: int = Form(...), db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=301)

    is_succeeded = classdata.update_marks(studentid=studentid, subjectid=subjectid, ise=ise, mse=mse, ese=ese, db=db)
    if is_succeeded == True:
        return RedirectResponse(f'/teacher/{subjectid}', status_code=303)
    return None



@router.get('/download_mark_template', status_code=302, description='Downloading template for marks')
async def download_template(request: Request, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=301)

    return FileResponse(settings.mark_template_path, media_type='text/csv',
                        filename='template_marks.csv')



# Uploading marks in a file
@router.post('/bulkmarks/{subjectid}', status_code=status.HTTP_201_CREATED, description='File is recieved in given formart and read and sent for validation with given criterion and sorted if successful on another page.')
async def bulk_load_marks(request: Request, subjectid: str, bulkfile: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role != 'TEACHER':
        return RedirectResponse('/404', status_code=301)

    bulk_list = await bulkfile.read()
    # File read function
    bulk_list = bulk_list.decode()
    # Converting encoded string to str
    marklist = bulk_list.split()
    # Splitting file at spaces and dropping first 5 places as per template
    marklist = marklist[5:]
    marklist = [mark.upper() for mark in marklist]
    summary = classdata.bulkupload_marks(marklist=marklist, subjectid=subjectid, db=db)
    return templates.TemplateResponse('protected/teacher/teacherloadsummary.html',
                                      {'request': request, 'summary': summary})
