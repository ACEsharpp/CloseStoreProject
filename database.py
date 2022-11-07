from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

host = 'localhost'
user = 'postgres'
password = 'imoshkuanysh'
database = "postgres"

SQLALCHEMY_DATABASE_URL = 'postgresql://' + user + ':' + password + '@' + host + "/" + database

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()