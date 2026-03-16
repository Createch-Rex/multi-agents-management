from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from database.db_base import DBBase
import config
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://%s:%s@%s:%s/%s"
SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL % (config.DATABASE_USER, quote_plus(config.DATABASE_PASSWORD), config.DATABASE_HOST, config.DATABASE_PORT, config.DATABASE_NAME)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
Base = declarative_base(cls=DBBase)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
