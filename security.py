from fastapi import Depends, FastAPI, HTTPException, status,Form,Response,Request
from datetime import datetime,timedelta
from passlib.context import CryptContext
from jose import JWTError,jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from database import Database

db=Database()

SECREAT_KEY='911c1b891e1b6efa34106a3b0203bc2c1ae262a9cb0aa843b1a5c8e2bd7cfff5'
ALGORITHM='HS256'
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://localhost:3000/",
    "http://192.168.0.128:3000/"
]

class FormData(BaseModel):
    username:str = Form(...)
    email:str = Form(...)
    password:str = Form(...)

class Token(BaseModel):
    access_token:str
class TokenData(BaseModel):
    email:str or None = None

class User(BaseModel):
    username:str
    email:str or None=None
    full_name:str or None=None
    disabled:bool or None=None
    # invalid_entries:int or None=None
class UserInDB(User):
    password:str


pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth_2_scheme=OAuth2PasswordBearer(tokenUrl='token')

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
def get_user(email:str):
    user_not_found_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='User not found',
        headers={'WWW-Authenticate':'Bearer'}
    )

    if db.get_user(email):
        user_data=db.get_user(email)
    else:
        raise user_not_found_exception
    return user_data

def authenticate_user(email:str,password:str):
    user=db.get_user(email)
    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='User not found',
        headers={'WWW-Authenticate':'Bearer'}
        )
    if not verify_password(password,user['password']):
        return False
    return user

def create_access_token(data:dict,expires_delta:timedelta or None = None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.utcnow() + expires_delta
    else:
        expire=datetime.utcnow()+timedelta(minutes=15)
    to_encode.update({'exp':expire})
    encoded_jwt=jwt.encode(to_encode,SECREAT_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token:str = Depends(oauth_2_scheme)):
    credential_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'}
    )
    try:
        payload=jwt.decode(token,SECREAT_KEY,algorithms=[ALGORITHM])
        email:str = payload.get('sub')
        if email is None:
            raise credential_exception
        token_data=TokenData(email=email)
    except JWTError as e:
        print(f'JWT error : {e}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate':'Bearer'}
        )
    user=get_user(email=token_data.email)
    if user is None:
        raise credential_exception
    return user

async def get_current_active_user(request:Request,current_user:UserInDB = Depends(get_current_user)):
   
    if current_user['disabled']:
        raise HTTPException(status_code=400,detail="Inactive user")
    return current_user