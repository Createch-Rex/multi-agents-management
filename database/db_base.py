from sqlalchemy import DateTime, Column
from sqlalchemy.orm import Session
import datetime
import uuid


class DBBase:
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def create(self):
        for item in self.__table__.columns:
            if item.primary_key:
                setattr(self, item.key, uuid.uuid4().hex)

    def get_dict(self):
        data = {}
        for item in self.__table__.columns:
            item_type = str(item.type)
            value = getattr(self, item.key, None)
            key = item.key
            if key == 'password':
                continue
            data[key] = value
            if item_type == "DATETIME" and value and isinstance(value, datetime.datetime):
                data[key] = int(value.timestamp() * 1000)
            elif item_type == "DATE" and value and isinstance(value, datetime.date):
                data[key] = value.strftime("%Y-%m-%d")
        return data

    def pre_delete(self, db: Session):
        pass
