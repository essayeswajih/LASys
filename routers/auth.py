from datetime import timedelta, datetime
from typing import Annotated
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette import status
from db.database import get_db
from models.usersEntity import User
from random import randint

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '1B63ECA66BFD46C13578C82E92DD4'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    firstName: str
    lastName: str
    company: str
    password: str
    email: str 


class Token(BaseModel):
    access_token: str
    token_type: str

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    if(validate_user_email(db,create_user_request.email)):
        user = User(
            firstName = create_user_request.firstName,
            lastName = create_user_request.lastName,
            company = create_user_request.company,
            email = create_user_request.email,
            username = generate_unique_username(db, create_user_request.firstName, create_user_request.lastName),
            hashed_password=bcrypt_context.hash(create_user_request.password)
        )
        db.add(user)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email exist."
        )
def authenticated_user(username: str, password: str, db: db_dependency):
    user = db.query(User).filter(
        or_(User.username == username, User.email == username)
    ).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post('/sign_in', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticated_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate user"
        )
    token = create_access_token(user.username, user.id, timedelta(days=30))
    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
            )
        return {"username": username, "id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

@router.get("/", status_code=status.HTTP_200_OK)
async def user(db: db_dependency, user_data: Annotated[dict, Depends(get_current_user)]):
    # Fetch user details from the database using the token payload
    user = db.query(User).filter_by(username=user_data["username"], id=user_data["id"]).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    # Return serialized user data
    return {"User": {"id": user.id, "username": user.username, "email": user.email, "role":user.role}}


def generate_unique_username(db, first_name, last_name):
    base_username = f"{first_name}.{last_name}_{randint(0, 999)}"
    while db.query(User).filter(User.username == base_username).first():
        base_username = f"{first_name}.{last_name}_{randint(0, 999)}"
    return base_username

def validate_user_email(db, email):
    return db.query(User).filter(User.email == email).first() is None

