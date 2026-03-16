from database.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import *


class Task(Base):
    __tablename__ = 'task'

    task_id = Column(String(255), primary_key=True)
    project_id = Column(String(255), comment="FK to project.project_id")
    title = Column(String(255))
    description = Column(Text)
    worker_id = Column(String(255), comment="FK to worker.worker_id")
    status = Column(String(255))
    chat_session = Column(String(255))

    def pre_delete(self, db: Session):
        pass
