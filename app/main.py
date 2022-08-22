from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routers import login, user, admin, student, teacher
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException


app = FastAPI(title="ABCXYZ School Results",
              version="0.1",
              description="This module is designed to make it easy for teachers to upload their final marks as well as for classteacher to review them as well as for students to see their result"
              )

templates = Jinja2Templates(directory="templates")
# Router is used to attach different apps to first process
app.include_router(login.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(teacher.router)
app.include_router(student.router)

# Rendering the home route
@app.get('/', status_code=200, response_class=HTMLResponse, description='This is the home route')
async def homepage(request: Request):
    return templates.TemplateResponse('unprotected/homepage.html', {'request': request, 'message': 'Welcome'})

# In case of authorization failure this template is rendered
@app.get('/404', status_code=200, response_class=HTMLResponse,
         description='This route is called when there is any unauthorised response like expiration of cookie, accessing unauthorised route etc.')
async def homepage(request: Request):
    return templates.TemplateResponse('unprotected/unauthorised.html', {'request': request, 'message': 'Unauthorised'})

@app.exception_handler(HTTPException)
async def my_custom_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse('unprotected/notfound.html', {'request': request})
    else:
        return await http_exception_handler(request, exc)
