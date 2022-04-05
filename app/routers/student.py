from fastapi import APIRouter, UploadFile,status, Depends, Form, Request, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from ..database.database import get_db
from fastapi.templating import Jinja2Templates
from ..database import model
from ..metadata import schema
from ..database.crud import subjectdata, userdata, classdata
from sqlalchemy.orm import Session
from ..auth.oauth2 import get_current_user
from ..utils.marks_validator import marks_validator

router = APIRouter(tags=['Student'])

templates = Jinja2Templates(directory="templates")


@router.get('/marksheet/{id}', status_code=status.HTTP_202_ACCEPTED, description='This route renders a marksheet for the student. Admin and student both can access this route')
def get_marklist(request : Request, id : str, db : Session = Depends(get_db)):
    token_data = None
    try:
        token : str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=303)
    if token_data.role not in  ('ADMIN', 'STUDENT'):
        return RedirectResponse('/404', status_code=303)
    student = userdata.get_student_from_id(id=id, db=db)

    if not student:
        return RedirectResponse('/404-unauthorised', status_code=status.HTTP_306_RESERVED)

    marks = classdata.get_all_marks_student(id = id, db=db)
    if not marks:
        return RedirectResponse('/404-unauthorised', status_code=status.HTTP_306_RESERVED)
    subjects = subjectdata.get_all_subjects(db=db)
    if not subjects:
        return RedirectResponse('/404-unauthorised', status_code=status.HTTP_306_RESERVED)

    maxmarks = 0

    for subject in subjects:
        maxmarks += subject.totalmax

    total_marks = 0

    for mark in marks:
        total_marks += mark.total

    finalgrade = marks_validator(int((total_marks/maxmarks)*100), str(model.DEFAULT_GRADE_PARAMETERS))
    return templates.TemplateResponse('marksheet.html' ,{'request' : request, 'student':student,'marks':marks, 'subjects':subjects, 'maxmarks':maxmarks, 'total_marks':total_marks, 'finalgrade':finalgrade, 'role':token_data.role})