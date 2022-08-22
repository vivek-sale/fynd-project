from pydantic import BaseSettings

DEFAULT_GRADE_PARAMETERS: dict = {'A+': [91, 100], 'A': [81, 90], 'B+': [76, 80], 'B': [71, 75], 'C+': [66, 70],
                                  'C': [61, 65], 'D': [51, 60], 'E': [41, 50], 'F': [1, 40]}


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    default_grade_parameters: str = str(DEFAULT_GRADE_PARAMETERS)
    mail_username: str
    mail_password: str
    mark_template_path: str
    student_template_path: str 

    class Config:
        env_file = ".env"


settings = Settings()
