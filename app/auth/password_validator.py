from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Bcrypt algorithm hashes the password
def hash(password: str):
    return pwd_context.hash(password)

# user provided pasword is hashed and compared against hashed password from db
def verify(passwd, hashpasswd):
    return pwd_context.verify(passwd, hashpasswd)
