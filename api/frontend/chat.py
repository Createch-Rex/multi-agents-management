from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from database.models import Chat, Task
from sqlalchemy.orm import Session
import uuid

chat_router = APIRouter()


@chat_router.post("/list")
@manage_utils.auth_required
async def list_chats(request: Request, db: Session = Depends(common.get_db)):
    """獲取 Chat 列表 (按 task_id 過濾)"""
    data = await request.json()

    task_id = data.get('task_id')
    if not task_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 task_id 參數")

    # 驗證 task 是否存在
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return common.standard_response(status="error", error_code=404, error_message="Task 不存在")

    page = data.get('page', 1)
    page_size = data.get('page_size', 50)
    search_key = data.get('search_key', None)

    # Build query
    query = db.query(Chat).filter(Chat.task_id == task_id)
    
    # Search by message content
    if search_key:
        search_pattern = f"%{search_key}%"
        query = query.filter(Chat.message.like(search_pattern))
    
    # Get total count
    total = query.count()

    # Order by created_at (oldest first for chat history)
    query = query.order_by(Chat.created_at.asc())
    
    # Calculate offset and apply pagination
    offset = (page - 1) * page_size
    chats = query.offset(offset).limit(page_size).all()
    
    # Format response
    chat_list = [c.get_dict() for c in chats]
    
    return common.standard_response(response_data={
        "chats": chat_list,
        "total": total,
        "page": page,
        "page_size": page_size
    })


@chat_router.post("/create")
@manage_utils.auth_required
async def create_chat(request: Request, db: Session = Depends(common.get_db)):
    """創建新 Chat 訊息"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()

    task_id = data.get('task_id')
    role = data.get('role', 'user')
    message = data.get('message', '')
    message_type = data.get('message_type', 'user')

    # Validate required fields
    if not task_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 task_id 參數")
    
    if not message:
        return common.standard_response(status="error", error_code=400, error_message="訊息不能為空")

    # 驗證 task 是否存在
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return common.standard_response(status="error", error_code=404, error_message="Task 不存在")

    # Validate role
    valid_roles = ['user', 'agent', 'system']
    if role not in valid_roles:
        return common.standard_response(status="error", error_code=400, error_message=f"role 必須是 {valid_roles} 之一")

    # Validate message_type
    valid_types = ['user', 'agent', 'system']
    if message_type not in valid_types:
        return common.standard_response(status="error", error_code=400, error_message=f"message_type 必須是 {valid_types} 之一")

    # Create new chat
    new_chat = Chat()
    new_chat.chat_id = uuid.uuid4().hex
    new_chat.task_id = task_id
    new_chat.role = role
    new_chat.message = message
    new_chat.message_type = message_type
    
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return common.standard_response(response_data={"chat": new_chat.get_dict()})


@chat_router.put("/update")
@manage_utils.auth_required
async def update_chat(request: Request, db: Session = Depends(common.get_db)):
    """更新 Chat 訊息"""
    data = await request.json()

    chat_id = data.get('chat_id')
    if not chat_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 chat_id 參數")

    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        return common.standard_response(status="error", error_code=404, error_message="Chat 不存在")

    # Update fields
    if 'message' in data:
        chat.message = data['message']
    
    if 'message_type' in data:
        valid_types = ['user', 'agent', 'system']
        if data['message_type'] not in valid_types:
            return common.standard_response(status="error", error_code=400, error_message=f"message_type 必須是 {valid_types} 之一")
        chat.message_type = data['message_type']

    db.commit()
    db.refresh(chat)

    return common.standard_response(response_data={"chat": chat.get_dict()})


@chat_router.delete("/delete")
@manage_utils.auth_required
async def delete_chat(request: Request, db: Session = Depends(common.get_db)):
    """刪除 Chat 訊息"""
    
    chat_id = request.query_params.get('chat_id', None)
    
    if not chat_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 chat_id 參數")

    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    
    if not chat:
        return common.standard_response(status="error", error_code=404, error_message="Chat 不存在")

    # Execute pre_delete hook
    chat.pre_delete(db)
    
    db.delete(chat)
    db.commit()
    
    return common.standard_response(response_data={"message": "Chat 已刪除"})