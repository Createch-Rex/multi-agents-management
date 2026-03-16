from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from sqlalchemy.orm import Session
from database.models import User, Project, ProjectWorker
from datetime import datetime

user_router = APIRouter()


@user_router.post("/list")
@manage_utils.auth_required
async def list_users(request: Request, db: Session = Depends(common.get_db)):
    """獲取用戶列表 (支持 pagination, search, filter)"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()

    # 只有 admin 可以查看所有用戶
    if user.role != 'admin':
        return common.standard_response(status="error", error_code=403, error_message="只有 admin 可以查看用戶列表")

    page = data.get('page', 1)
    page_size = data.get('page_size', 20)
    search_key = data.get('search_key', None)
    role = data.get('role', None)

    # Build query
    query = db.query(User)
    
    # Filter by role
    if role:
        query = query.filter(User.role == role)
    
    # Search by username or email
    if search_key:
        search_pattern = f"%{search_key}%"
        query = query.filter(
            (User.username.like(search_pattern)) | 
            (User.email.like(search_pattern))
        )
    
    # Get total count BEFORE applying pagination
    total = query.count() + 0
    
    # Order by created_at (newest first) before pagination
    query = query.order_by(User.created_at.desc())
    
    # Calculate offset and apply pagination
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()
    
    # Format response (唔好返回 password)
    user_list = []
    for u in users:
        user_dict = u.get_dict()
        user_list.append(user_dict)
    
    return common.standard_response(response_data={
        "users": user_list,
        "total": total
    })


@user_router.get("/get")
@manage_utils.auth_required
async def get_user(request: Request, db: Session = Depends(common.get_db)):
    """獲取單一用戶詳情"""
    current_user = manage_utils.get_system_user_from_header(request, db)
    user_id = request.query_params.get('user_id', None)
    
    if not user_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 user_id 參數")
    
    # 普通用戶只能查看自己
    if current_user.role != 'admin' and current_user.user_id != user_id:
        return common.standard_response(status="error", error_code=403, error_message="無權限查看其他用戶")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        return common.standard_response(status="error", error_code=404, error_message="用戶不存在")
    
    # 唔好返回 password
    user_dict = user.get_dict()
    
    return common.standard_response(response_data={"user": user_dict})


@user_router.post("/create")
@manage_utils.auth_required
async def create_user(request: Request, db: Session = Depends(common.get_db)):
    """創建新用戶 (只有 admin 可以)"""
    current_user = manage_utils.get_system_user_from_header(request, db)
    
    if current_user.role != 'admin':
        return common.standard_response(status="error", error_code=403, error_message="只有 admin 可以創建用戶")
    
    data = await request.json()
    
    username = data.get('username', '')
    password = data.get('password', '')
    role = data.get('role', 'user')
    email = data.get('email', '')
    
    if not username:
        return common.standard_response(status="error", error_code=400, error_message="用戶名不能为空")
    
    if not password:
        return common.standard_response(status="error", error_code=400, error_message="密碼不能为空")
    
    # 檢查用戶名是否已經存在
    existing = db.query(User).filter(User.username == username).first()
    
    if existing:
        return common.standard_response(status="error", error_code=409, error_message="呢個用戶名已經存在")
    
    # 創建新用戶
    new_user = User()
    new_user.username = username
    new_user.password = User.generate_password(password)
    new_user.role = role
    new_user.email = email
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 唔好返回 password
    user_dict = new_user.get_dict()
    
    return common.standard_response(response_data={"user": user_dict})


@user_router.put("/update")
@manage_utils.auth_required
async def update_user(request: Request, db: Session = Depends(common.get_db)):
    """更新用戶資料"""
    current_user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    user_id = data.get('user_id', None)
    
    if not user_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 user_id 參數")
    
    # 普通用戶只能更新自己
    if current_user.role != 'admin' and current_user.user_id != user_id:
        return common.standard_response(status="error", error_code=403, error_message="無權限修改其他用戶")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        return common.standard_response(status="error", error_code=404, error_message="用戶不存在")
    
    # 更新字段
    if 'username' in data and current_user.role == 'admin':
        # 檢查新用戶名是否已經存在
        existing = db.query(User).filter(User.username == data['username']).first()
        if existing and existing.user_id != user_id:
            return common.standard_response(status="error", error_code=409, error_message="呢個用戶名已經存在")
        user.username = data['username']
    
    if 'email' in data:
        user.email = data['email']
    
    # 只有 admin 可以改 role
    if 'role' in data and current_user.role == 'admin':
        user.role = data['role']
    
    # 更新密碼 (可選)
    if 'password' in data and data['password']:
        user.password = User.generate_password(data['password'])
    
    db.commit()
    db.refresh(user)
    
    # 唔好返回 password
    user_dict = user.get_dict()
    
    return common.standard_response(response_data={"user": user_dict})


@user_router.delete("/delete")
@manage_utils.auth_required
async def delete_user(request: Request, db: Session = Depends(common.get_db)):
    """刪除用戶 (只有 admin 可以)"""
    current_user = manage_utils.get_system_user_from_header(request, db)
    
    if current_user.role != 'admin':
        return common.standard_response(status="error", error_code=403, error_message="只有 admin 可以刪除用戶")
    
    user_id = request.query_params.get('user_id', None)
    
    if not user_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 user_id 參數")
    
    # 唔可以刪除自己
    if user_id == current_user.user_id:
        return common.standard_response(status="error", error_code=400, error_message="唔可以刪除自己")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        return common.standard_response(status="error", error_code=404, error_message="用戶不存在")
    
    # 檢查是否有 projects
    projects_count = db.query(Project).filter(Project.owner_id == user_id).count()
    
    if projects_count > 0:
        return common.standard_response(status="error", error_code=409, error_message=f"呢個用戶仲有 {projects_count} 個項目，唔可以刪除")
    
    # 檢查是否有 worker assignments
    assignments_count = db.query(ProjectWorker).filter(ProjectWorker.assigned_by == user_id).count()
    
    if assignments_count > 0:
        return common.standard_response(status="error", error_code=409, error_message=f"呢個用戶仲有 {assignments_count} 個 Worker 分配記錄")
    
    # 執行 pre_delete hook (如果有)
    user.pre_delete(db)
    
    db.delete(user)
    db.commit()
    
    return common.standard_response(response_data={"message": "用戶已刪除"})
