from sqlalchemy import Integer, String, Column, ForeignKey, Enum
from db.database import Base
from enum import Enum as PyEnum


class RoleEnum(PyEnum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key = True, autoincrement = True, index= True)
    username = Column(String, unique=True)
    firstName = Column(String)
    lastName = Column(String)
    company = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    email = Column(String,unique = True)
    hashed_password = Column(String)