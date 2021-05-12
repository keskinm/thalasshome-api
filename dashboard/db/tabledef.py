# from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///providers.db', echo=True)
Base = declarative_base()


class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    email = Column(String(100), unique=True)
    country = Column(String)
    zone = Column(String)
    phone_number = Column(String)

    def __init__(self, username, password, email, country, zone, phone_number):
        self.username = username
        self.password = password
        self.email = email
        self.country = country
        self.zone = zone
        self.phone_number = phone_number

# create tables
Base.metadata.create_all(engine)

