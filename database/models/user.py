from database.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import *
import hashlib


class User(Base):
    __tablename__ = 'user'

    user_id = Column(String(255), primary_key=True)
    username = Column(String(255))
    password = Column(Text)

    def pre_delete(self, db: Session):
        pass

    @staticmethod
    def generate_password(password: str):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
