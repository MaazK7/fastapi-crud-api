from sqlalchemy import String,Integer,Column,Boolean

from database import Base


class Person(Base):
    __tablename__="person"
    id= Column(Integer,primary_key=True) 
    first_name= Column(String(40),nullable=False)
    last_name=Column(String(40))
    isMale=Column(Boolean(40))

