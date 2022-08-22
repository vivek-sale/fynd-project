from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ..metadata.config import settings

# Database connection string
SQLALCHEMY_DB_URL = f'mysql+pymysql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DB_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# It is used to bind tables to database
Base = declarative_base()


# Fetch yielded session of db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# try:
#     engine.connect()
#     print('success')
# except SQLAlchemyError as e:
#     print(e)
