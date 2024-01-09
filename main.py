from asyncio import run
from fastapi import Depends, FastAPI, HTTPException, status,Form,Response,Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime,timedelta
from jose import JWTError,jwt
from passlib.context import CryptContext
from database import Database
from security import *
from sendMail import Mail
from model import Model
import amazon_scraper

db=Database()
ai=Model()
# mail=Mail()

ACCESS_TOKEN_EXPIRE_MINUTES=40
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://localhost:3000/",
    "http://192.168.0.128:3000/",
    "https://miraparentpal.com",
    "https://www.miraparentpal.com",
    'https://miraparentpal.vercel.app'
]

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# db={
#     'vishnu@gmail.com':{
#         'username':'vishnu',
#         'full_name':'vishnu vardhan gowd',
#         'email':'vishnu@gmail.com',
#         'password':'$2b$12$1wWBGtrpd.I97eZYVyjG4ukcQTaszhV3Azmz4S5MGXo2ZJfqSxClm',
#         'disabled':False,
#         'invalid_entries':0
#     }
# }
class FormData(BaseModel):
    username:str = Form(...)
    email:str = Form(...)
    password:str = Form(...)

class Token(BaseModel):
    access_token:str
    email:str
    username:str
class TokenData(BaseModel):
    email:str or None = None

class User(BaseModel):
    username:str
    email:str or None=None
    full_name:str or None=None
    disabled:bool or None=None
    invalid_entries:int or None=None
class UserInDB(User):
    password:str
def calAge(date_of_birth):
    current_date = datetime.now()
    age = current_date - date_of_birth
    years = age.days // 365
    months = ((age.days % 365) - years // 4) // 30
    days = ((age.days % 365) - years // 4) % 30
    return years, months, days



@app.post('/auth/signin/',response_model=Token)
async def login_for_access_token(request: Request,form_data:OAuth2PasswordRequestForm = Depends()):
    print(request.headers.get ('referer'),'************')
    
    user=authenticate_user(form_data.username,form_data.password)
    print(user)
    if not user:
        # return {'status_code':'401_UNAUTHORIZED','details':'Incorrect username or password'}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate':'Bearer'}
        )
    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(
        data={'sub':user['email']},
        expires_delta=access_token_expires
    )

    return {'access_token':access_token,'email':user['email'],'username':user['username']}

@app.post('/auth/signup/')
async def signup(request : Request):
    
    payload = await request.form()
    payload=dict(payload)
    payload['password']=get_password_hash(payload['password'])
    user_details=payload
    # user_details={
    #     'username':username,
    #     'email':email,
    #     'password':get_password_hash(password)
    # }
    state=db.insert_user(user_details)
    return state
@app.post('/sendOTP/')
async def getOTP(request:Request,username:str = Form(...),email:str = Form(...)):
    user=db.get_user(email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User already exists. ',
            headers={'WWW-Authenticate':'Bearer'}
        )
    mail=Mail()
    otp,msg=mail.sendOTP(username,email)
    print(otp,msg)
    if otp==None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'{msg}',
            headers={'WWW-Authenticate':'Bearer'}
        )
    return otp

@app.post('/chat/')
async def chat(request:Request,query:str=Form(...),current_user:User = Depends(get_current_active_user)):
    print(current_user)
    print(current_user['email'],query)
    userdata=current_user
    year,month,day=[int(x) for x in userdata['babyDOB'].split('-')]
    date_of_birth = datetime(year,month,day)
    userdata['ayears'],userdata['amonths'],userdata['adays']=calAge(date_of_birth)
    print(query,userdata['ayears'],userdata['amonths'])
    prod_rec,response=ai.quering(query,userdata)
    if prod_rec:
        products=amazon_scraper.start_scrape(response)
        print(type(products),len(products))
        message={'response':products,'products':True}   
        return message
    
    message={'response':response,'products':False}
    print(message)
    return message

@app.get('/user/me/')
async def read_user_me(current_user:User = Depends(get_current_active_user)):
    return current_user

@app.get('/user/me/items')
async def read_items(current_user:User = Depends(get_current_active_user)):
    return [{'item_id':1,'owner':current_user}]


