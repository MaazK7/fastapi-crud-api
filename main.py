from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from database import SessionLocal
import models
from models import Base
from database import engine
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import *
from datetime import timedelta
from typing import Annotated

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()
db = SessionLocal()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "role": "admin",
        "hashed_password": "$2b$12$tJD64mRe0bd/UNdAANZtvuOnWDKScbVtXA9lB6X7arZxJQbAyMbd2",
        "disabled": False,
    },
    
        "alex123": {
        "username": "alex123",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "role": "user",
        "hashed_password": "$2b$12$tJD64mRe0bd/UNdAANZtvuOnWDKScbVtXA9lB6X7arZxJQbAyMbd2",
        "disabled": False,
    }
}

class OurBaseModel(BaseModel):

    class Config:
        orm_mode = True

class Person(OurBaseModel):

    id: int
    first_name: str | None = None
    last_name: str
    isMale: bool

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get(
    "/", response_model=list[Person], status_code=status.HTTP_200_OK, tags=["Get_Info"]
)
def get_all_persons(current_user: dict = Depends(get_current_active_user)):
    persons = db.query(models.Person).all()

    return persons


@app.post("/addperson", response_model=Person, status_code=status.HTTP_201_CREATED)
def add_person(person: Person, _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))]):

    new_person = models.Person(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        isMale=person.isMale,
    )

    find_person = db.query(models.Person).filter(models.Person.id == person.id).first()

    if find_person:
        raise HTTPException(
            status_code=401, detail="Already a record with same information."
        )

    else:

        db.add(new_person)
        db.commit()

    return person


@app.delete(
    "/delperson/{id}", response_model=Person, status_code=status.HTTP_201_CREATED
)
def add_person(id: int, current_user: dict = Depends(get_current_active_user)):

    temp_person = db.query(models.Person).filter(models.Person.id == id).first()

    if temp_person:
        db.delete(temp_person)
        db.commit()

    else:
        raise HTTPException(status_code=401, detail="No record found.")

    return temp_person


