from database.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import *


class Worker(Base):
    __tablename__ = 'worker'

    worker_id = Column(String(255), primary_key=True)
    agent_id = Column(String(255))
    role = Column(String(255))
    system_prompt = Column(Text)
    token = Column(String(255))
    heartbeat_interval = Column(Integer, default=300)
    status = Column(String(50), default="offline", comment="Enum: online/offline/busy")
    last_heartbeat = Column(DateTime, comment="Last heartbeat timestamp")
    capabilities = Column(Text, comment="JSON array of skills")
    max_concurrent_tasks = Column(Integer, default=1)

    def pre_delete(self, db: Session):
        pass
