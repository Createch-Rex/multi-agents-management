from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from sqlalchemy.orm import Session
from database.models import Worker, ProjectWorker
import json

worker_router = APIRouter()


@worker_router.post("/list")
@manage_utils.auth_required
async def list_workers(request: Request, db: Session = Depends(common.get_db)):
    """獲取 Worker 列表 (支持 pagination, search, filter)"""
    data = await request.json()

    page = data.get('page', 1)
    page_size = data.get('page_size', 20)
    search_key = data.get('search_key', None)
    status = data.get('status', None)
    role = data.get('role', None)

    # Build query
    query = db.query(Worker)
    
    # Filter by status
    if status:
        query = query.filter(Worker.status == status)
    
    # Filter by role
    if role:
        query = query.filter(Worker.role == role)
    
    # Search by agent_id or role
    if search_key:
        search_pattern = f"%{search_key}%"
        query = query.filter(
            (Worker.agent_id.like(search_pattern)) | 
            (Worker.role.like(search_pattern))
        )
    
    # Get total count BEFORE applying pagination
    total = query.count() + 0
    
    # Order by created_at (newest first) before pagination
    query = query.order_by(Worker.created_at.desc())
    
    # Calculate offset and apply pagination
    offset = (page - 1) * page_size
    workers = query.offset(offset).limit(page_size).all()
    
    # Format response
    worker_list = [w.get_dict() for w in workers]
    
    return common.standard_response(response_data={
        "workers": worker_list,
        "total": total
    })


@worker_router.get("/get")
@manage_utils.auth_required
async def get_worker(request: Request, db: Session = Depends(common.get_db)):
    """獲取單一 Worker 詳情"""
    worker_id = request.query_params.get('worker_id', None)
    
    if not worker_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 worker_id 參數")
    
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    
    if not worker:
        return common.standard_response(status="error", error_code=404, error_message="Worker 不存在")
    
    return common.standard_response(response_data={"worker": worker.get_dict()})


@worker_router.post("/create")
@manage_utils.auth_required
async def create_worker(request: Request, db: Session = Depends(common.get_db)):
    """創建新 Worker"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    agent_id = data.get('agent_id', '')
    role = data.get('role', 'worker')
    system_prompt = data.get('system_prompt', '')
    token = data.get('token', '')
    heartbeat_interval = data.get('heartbeat_interval', 300)
    capabilities = data.get('capabilities', [])
    max_concurrent_tasks = data.get('max_concurrent_tasks', 1)
    
    if not agent_id:
        return common.standard_response(status="error", error_code=400, error_message="Agent ID 不能为空")
    
    # 創建新 Worker
    new_worker = Worker()
    new_worker.agent_id = agent_id
    new_worker.role = role
    new_worker.system_prompt = system_prompt
    new_worker.token = token
    new_worker.heartbeat_interval = heartbeat_interval
    new_worker.capabilities = json.dumps(capabilities) if isinstance(capabilities, list) else capabilities
    new_worker.max_concurrent_tasks = max_concurrent_tasks
    new_worker.status = "online"
    
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    
    return common.standard_response(response_data={"worker": new_worker.get_dict()})


@worker_router.put("/update")
@manage_utils.auth_required
async def update_worker(request: Request, db: Session = Depends(common.get_db)):
    """更新 Worker 資料"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    worker_id = data.get('worker_id', None)
    
    if not worker_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 worker_id 參數")
    
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    
    if not worker:
        return common.standard_response(status="error", error_code=404, error_message="Worker 不存在")
    
    # 更新字段
    if 'agent_id' in data:
        worker.agent_id = data['agent_id']
    if 'role' in data:
        worker.role = data['role']
    if 'system_prompt' in data:
        worker.system_prompt = data['system_prompt']
    if 'token' in data:
        worker.token = data['token']
    if 'heartbeat_interval' in data:
        worker.heartbeat_interval = data['heartbeat_interval']
    if 'status' in data:
        worker.status = data['status']
    if 'last_heartbeat' in data:
        worker.last_heartbeat = data['last_heartbeat']
    if 'capabilities' in data:
        worker.capabilities = json.dumps(data['capabilities']) if isinstance(data['capabilities'], list) else data['capabilities']
    if 'max_concurrent_tasks' in data:
        worker.max_concurrent_tasks = data['max_concurrent_tasks']
    
    db.commit()
    db.refresh(worker)
    
    return common.standard_response(response_data={"worker": worker.get_dict()})


@worker_router.delete("/delete")
@manage_utils.auth_required
async def delete_worker(request: Request, db: Session = Depends(common.get_db)):
    """刪除 Worker"""
    user = manage_utils.get_system_user_from_header(request, db)
    worker_id = request.query_params.get('worker_id', None)
    
    if not worker_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 worker_id 參數")
    
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    
    if not worker:
        return common.standard_response(status="error", error_code=404, error_message="Worker 不存在")
    
    # 檢查是否有 active assignments
    active_assignments = db.query(ProjectWorker).filter(
        ProjectWorker.worker_id == worker_id,
        ProjectWorker.status == "active"
    ).count()
    
    if active_assignments > 0:
        return common.standard_response(status="error", error_code=409, error_message=f"呢個 Worker 仲有 {active_assignments} 個 active 分配，唔可以刪除")
    
    # 執行 pre_delete hook (如果有)
    worker.pre_delete(db)
    
    db.delete(worker)
    db.commit()
    
    return common.standard_response(response_data={"message": "Worker 已刪除"})


@worker_router.post("/heartbeat")
async def worker_heartbeat(request: Request, db: Session = Depends(common.get_db)):
    """Worker 心跳接口 (更新 last_heartbeat)"""
    data = await request.json()
    worker_id = data.get('worker_id')
    status = data.get('status', 'online')
    
    if not worker_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 worker_id")
    
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    
    if not worker:
        return common.standard_response(status="error", error_code=404, error_message="Worker 不存在")
    
    # 更新心跳時間同狀態
    from datetime import datetime
    worker.last_heartbeat = datetime.now()
    worker.status = status
    
    db.commit()
    db.refresh(worker)

    # start worker session to complete assigned tasks
    
    return common.standard_response(response_data={
        "message": "心跳更新成功",
        "worker_id": worker_id,
        "status": status
    })
