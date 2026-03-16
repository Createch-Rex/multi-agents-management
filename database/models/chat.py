from database.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import *


class Chat(Base):
    __tablename__ = 'chat'

    chat_id = Column(String(255), primary_key=True)
    task_id = Column(String(255), comment="FK to task.task_id")
    role = Column(String(255))
    message = Column(Text)
    message_type = Column(String(50), comment="Enum: user/agent/system")

    def pre_delete(self, db: Session):
        pass
