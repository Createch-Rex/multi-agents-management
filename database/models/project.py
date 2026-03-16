from database.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import *


class Project(Base):
    __tablename__ = 'project'

    project_id = Column(String(255), primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    status = Column(String(255))
    workspace_path = Column(Text)
    owner_id = Column(String(255), comment="FK to user.user_id")
    tags = Column(Text, comment="JSON array for categorization")

    def pre_delete(self, db: Session):
        pass
