from fastapi import APIRouter, status, Request, Response, Form, Depends
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.database.crud.logindata import get_user
from app.auth.password_validator import verify, hash
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.auth.oauth2 import create_access_token, get_current_user

router = APIRouter(tags=['login'])
templates = Jinja2Templates(directory="templates")


@router.post('/login', status_code=status.HTTP_202_ACCEPTED,
             description='Used to get username and password from form, check it and assign cookies for it and route the user according to role')
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(username=user_credentials.username, db=db)
    # Getting form data in oauth2 schema
    if not user:
        # For empty user
        return RedirectResponse(url='/login?invalid=True', status_code=status.HTTP_303_SEE_OTHER)
    if not verify(user_credentials.password, user.password):
        # For password mismatch invalid=True unhides hidden attribute from front end
        return RedirectResponse(url='/login?invalid=True', status_code=303)

    access_token = create_access_token(data={'user': user.id, 'role': user.role})

    # Role is fetched and assigned to different routed based on different roles
    if user.role == 'ADMIN':
        response = RedirectResponse('/admin/home', status_code=status.HTTP_302_FOUND)
        # Cookie is sent and passed through response for each role
        response.set_cookie('access_token', value=access_token, httponly=True)
        return response
    elif user.role == 'TEACHER':
        response = RedirectResponse('/teacher', status_code=302)
        response.set_cookie('access_token', value=access_token, httponly=True)
        return response
    elif user.role == 'STUDENT':
        response = RedirectResponse(f'/marksheet/{user.id}', status_code=302)
        response.set_cookie('access_token', value=access_token, httponly=True)
        return response


# Rendering login page
@router.get('/login', status_code=status.HTTP_202_ACCEPTED, description='Used to render the login page')
async def user_login(request: Request, invalid: bool = False):
    return templates.TemplateResponse('unprotected/login.html', {'request': request, 'invalid': invalid})



# Deleting cookie and redirecting to login page
@router.get('/logout', description='Used for deleting the cookie assigned to user')
async def user_logout(request: Request, response: Response):
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie('access_token')
    return response



# Rendering chaneg password page
@router.get('/changepassword', status_code=302, description='Used to render change password page')
async def user_change_password(request: Request, invalid: bool = False, db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role not in ('ADMIN', 'TEACHER'):
        return RedirectResponse('/404', status_code=301)
    return templates.TemplateResponse('protected/change_password.html',
                                      {'request': request, 'role': token_data.role, 'invalid': invalid})


# Old and new password is fetched from front end form
@router.post('/changepassword', status_code=302,
             description='Old password is checked , new password is hashed and updated in login db.')
async def chnage_password(request: Request, old_password: str = Form(...), new_password: str = Form(...),
                          db: Session = Depends(get_db)):
    token_data = None
    try:
        token: str = request.cookies.get('access_token')
        token_data = get_current_user(session=token, db=db)
    except Exception as e:
        return RedirectResponse('/404', status_code=301)
    if token_data.role not in ('ADMIN', 'TEACHER'):
        return RedirectResponse('/404', status_code=301)

    user = get_user(username=token_data.id, db=db)
    # Getting userdata
    if not user:
        # Similar to login
        return RedirectResponse(url='/changepassword?invalid=True', status_code=301)
    if not verify(old_password, user.password):
        return RedirectResponse(url='/changepassword?invalid=True', status_code=301)
    # New password is hashed and sent to db
    user.password = hash(new_password)
    db.commit()
    if token_data.role == 'ADMIN':
        # Redirecting to different pagees based on role of arriving
        return RedirectResponse('/admin/home', status_code=302)
    else:
        return RedirectResponse('/teacher', status_code=302)
