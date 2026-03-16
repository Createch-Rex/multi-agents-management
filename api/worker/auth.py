from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from sqlalchemy.orm import Session
from database.models import Worker, ProjectWorker
import uuid

auth_router = APIRouter()


@auth_router.get("/activate")
async def list_workers(request: Request, agent_id: str, db: Session = Depends(common.get_db)):
    worker = db.query(Worker).filter(Worker.agent_id == agent_id).first()

    if not worker:
        return common.standard_response(status="error", error_code=403, error_message="Worker不存在")

    if worker.token:
        return common.standard_response(status="error", error_code=403, error_message="Worker已被激活")

    worker.token = uuid.uuid4().hex
    db.commit()
    return common.standard_response(response_data={"token": worker.token})