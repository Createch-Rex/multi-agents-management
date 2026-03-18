from database.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import *


class ProjectWorker(Base):
    __tablename__ = 'project_worker'

    project_id = Column(String(255), ForeignKey('project.project_id'), primary_key=True)
    worker_id = Column(String(255), ForeignKey('worker.worker_id'), primary_key=True)
    assigned_at = Column(DateTime, default=func.now(), comment="Assignment timestamp")
    assigned_by = Column(String(255), comment="FK to user.user_id who assigned")
    status = Column(String(255), default="active", comment="Enum: active/inactive/removed")

    def pre_delete(self, db: Session):
        pass
