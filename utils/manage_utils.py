from database.models import User, Worker
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
from functools import wraps
from utils import common
import config
import jwt


def get_system_user_from_header(request: Request, db: Session) -> Optional[User]:
    token = request.headers.get('Authorization')
    if not token:
        return None

    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, config.SYSTEM_KEY, algorithms=['HS256'])
    except:
        return None

    user_id = payload.get('user_id', None)
    if not user_id:
        return None

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None

    return user

def auth_required(func):
    @wraps(func)
    async def wrapper(request: Request, db: Session = Depends(common.get_db), *args, **kwargs):
        user = get_system_user_from_header(request, db)
        if not user:
            return common.standard_response(status="expire")
        kwargs['db'] = db
        kwargs['request'] = request
        response = await func(*args, **kwargs)
        db.commit()
        return response
    return wrapper


def get_worker_from_header(request: Request, db: Session) -> Optional[Worker]:
    token = request.headers.get('X-Worker-Token')
    if not token:
        return None

    worker = db.query(Worker).filter(Worker.token == token).first()
    if not worker:
        return None
    return worker


def worker_auth_required(func):
    @wraps(func)
    async def wrapper(request: Request, db: Session = Depends(common.get_db), *args, **kwargs):
        worker = get_worker_from_header(request, db)
        if not worker:
            return common.standard_response(status="expire")
        kwargs['db'] = db
        kwargs['request'] = request
        response = await func(*args, **kwargs)
        db.commit()
        return response
    return wrapper