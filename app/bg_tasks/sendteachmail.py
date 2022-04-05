from fastapi_mail import MessageSchema, FastMail, ConnectionConfig
from fastapi import BackgroundTasks
from ..metadata.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD= settings.mail_password,
    MAIL_FROM=settings.mail_username,
    MAIL_PORT = 587,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_TLS=True,
    MAIL_SSL=False
)


def send_mail_to_teacher(backgroundtask : BackgroundTasks, emailid : str, name : str, subject : str):
    message = MessageSchema(
        subject=f'Admin has invited you to contribute on {subject} for class 7',
        recipients=[emailid],
        body=f"""
            <h3>Admin has invited {name} to contribute on {subject} for class 7</h3>
            <p>Use your date of birth for password in yyyy-mm-dd format</p>
            <p>It is recommended that you change your password</p>
        """,
        subtype='html',
    )
    fm = FastMail(conf)
    backgroundtask.add_task(fm.send_message, message)
