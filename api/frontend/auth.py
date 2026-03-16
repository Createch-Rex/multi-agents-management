from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from sqlalchemy.orm import Session
from database.models import *
import config
import jwt

auth_router = APIRouter()


@auth_router.get("/check_auth")
@manage_utils.auth_required
async def check_auth(request: Request, db: Session = Depends(common.get_db)):
    user = manage_utils.get_system_user_from_header(request, db)
    payload = {'user_id': user.user_id}
    token = jwt.encode(payload, config.SYSTEM_KEY, algorithm='HS256')
    return common.standard_response(response_data={"token": token})


@auth_router.post("/login")
async def login(request: Request, db: Session = Depends(common.get_db)):
    data = await request.json()
    username = data.get('username', '')
    password = data.get('password', '')
    user = db.query(User).filter(User.username == username, User.password == User.generate_password(password)).first()

    if not user:
        return common.standard_response(status="error", error_code=400, error_message="使用者名稱或密碼不正確")

    payload = {'user_id': user.user_id}
    token = jwt.encode(payload, config.SYSTEM_KEY, algorithm='HS256')
    return common.standard_response(response_data={"token": token})


@auth_router.get('/profile')
@manage_utils.auth_required
async def get_profile(request: Request, db: Session = Depends(common.get_db)):
    user = manage_utils.get_system_user_from_header(request, db)
    return common.standard_response(response_data={"user": user.get_dict()})
