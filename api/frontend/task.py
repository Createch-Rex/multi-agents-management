from database.models import Task, Project, Worker
from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from sqlalchemy.orm import Session
from datetime import datetime

task_router = APIRouter()


@task_router.post("/list")
@manage_utils.auth_required
async def list_tasks(request: Request, db: Session = Depends(common.get_db)):
    """獲取任務列表 (支持 pagination, search, filter)"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()

    page = data.get('page', 1)
    page_size = data.get('page_size', 20)
    search_key = data.get('search_key', None)
    project_id = data.get('project_id', None)
    status = data.get('status', None)
    worker_id = data.get('worker_id', None)

    # Build query - only get tasks from projects user owns or is assigned to
    if user.role == 'admin':
        query = db.query(Task)
    else:
        # Non-admin: only tasks from projects they own
        query = db.query(Task).join(Project, Task.project_id == Project.project_id).filter(Project.owner_id == user.user_id)
    
    # Filter by project_id
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    # Filter by status
    if status:
        query = query.filter(Task.status == status)
    
    # Filter by worker_id
    if worker_id:
        query = query.filter(Task.worker_id == worker_id)
    
    # Search by title or description
    if search_key:
        search_pattern = f"%{search_key}%"
        query = query.filter(
            (Task.title.like(search_pattern)) | 
            (Task.description.like(search_pattern))
        )
    
    # Get total count
    total = query.count()
    
    # Order by created_at (newest first)
    query = query.order_by(Task.created_at.desc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    tasks = query.offset(offset).limit(page_size).all()
    
    # Format response
    task_list = [t.get_dict() for t in tasks]
    
    return common.standard_response(response_data={
        "tasks": task_list,
        "total": total
    })


@task_router.get("/get")
@manage_utils.auth_required
async def get_task(request: Request, db: Session = Depends(common.get_db)):
    """獲取單一任務詳情"""
    task_id = request.query_params.get('task_id', None)
    
    if not task_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 task_id 參數")
    
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return common.standard_response(status="error", error_code=404, error_message="任務不存在")
    
    return common.standard_response(response_data={"task": task.get_dict()})


@task_router.post("/create")
@manage_utils.auth_required
async def create_task(request: Request, db: Session = Depends(common.get_db)):
    """創建新任務"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    project_id = data.get('project_id')
    title = data.get('title', '')
    description = data.get('description', '')
    worker_id = data.get('worker_id', None)
    status = data.get('status', 'pending')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date', None)
    parent_task_id = data.get('parent_task_id', None)
    
    if not project_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 project_id 參數")
    
    if not title:
        return common.standard_response(status="error", error_code=400, error_message="任務標題不能為空")
    
    # 驗證項目存在
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        return common.standard_response(status="error", error_code=404, error_message="項目不存在")
    
    # 驗證 worker 如果有提供的話
    if worker_id:
        worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
        if not worker:
            return common.standard_response(status="error", error_code=404, error_message="Worker 不存在")
    
    # 創建新任務
    new_task = Task()
    new_task.project_id = project_id
    new_task.title = title
    new_task.description = description
    new_task.worker_id = worker_id
    new_task.status = status
    new_task.priority = priority
    new_task.parent_task_id = parent_task_id
    
    if due_date:
        new_task.due_date = datetime.fromisoformat(due_date)
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return common.standard_response(response_data={"task": new_task.get_dict()})


@task_router.put("/update")
@manage_utils.auth_required
async def update_task(request: Request, db: Session = Depends(common.get_db)):
    """更新任務資料"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    task_id = data.get('task_id', None)
    
    if not task_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 task_id 參數")
    
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return common.standard_response(status="error", error_code=404, error_message="任務不存在")
    
    # 更新字段
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'worker_id' in data:
        task.worker_id = data['worker_id']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'parent_task_id' in data:
        task.parent_task_id = data['parent_task_id']
    
    db.commit()
    db.refresh(task)
    
    return common.standard_response(response_data={"task": task.get_dict()})


@task_router.delete("/delete")
@manage_utils.auth_required
async def delete_task(request: Request, db: Session = Depends(common.get_db)):
    """刪除任務"""
    user = manage_utils.get_system_user_from_header(request, db)
    task_id = request.query_params.get('task_id', None)
    
    if not task_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 task_id 參數")
    
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return common.standard_response(status="error", error_code=404, error_message="任務不存在")
    
    # 執行 pre_delete hook
    task.pre_delete(db)
    
    db.delete(task)
    db.commit()
    
    return common.standard_response(response_data={"message": "任務已刪除"})
