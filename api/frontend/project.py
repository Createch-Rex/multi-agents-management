from fastapi import APIRouter, Request, Depends
from utils import common, manage_utils
from sqlalchemy.orm import Session
from database.models import Project, User, Worker
import config
import jwt
import json

project_router = APIRouter()


@project_router.post("/list")
@manage_utils.auth_required
async def list_projects(request: Request, db: Session = Depends(common.get_db)):
    data = await request.json()

    page = data.get('page', 1)
    page_size = data.get('page_size', 20)
    search_key = data.get('search_key', None)

    rep = []

    
    return common.standard_response(response_data={"projects": rep})


@project_router.get("/get")
@manage_utils.auth_required
async def get_project(request: Request, db: Session = Depends(common.get_db)):
    """獲取單一項目詳情"""
    project_id = request.query_params.get('project_id', None)
    
    if not project_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 project_id 參數")
    
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        return common.standard_response(status="error", error_code=404, error_message="項目不存在")
    
    return common.standard_response(response_data={"project": project.get_dict()})


@project_router.post("/create")
@manage_utils.auth_required
async def create_project(request: Request, db: Session = Depends(common.get_db)):
    """創建新項目"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    name = data.get('name', '')
    description = data.get('description', '')
    status = data.get('status', 'active')
    workspace_path = data.get('workspace_path', '')
    tags = data.get('tags', [])
    
    if not name:
        return common.standard_response(status="error", error_code=400, error_message="項目名稱不能为空")
    
    # 創建新項目
    new_project = Project()
    new_project.name = name
    new_project.description = description
    new_project.status = status
    new_project.workspace_path = workspace_path
    new_project.owner_id = user.user_id
    new_project.tags = json.dumps(tags) if isinstance(tags, list) else tags
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return common.standard_response(response_data={"project": new_project.get_dict()})


@project_router.put("/update")
@manage_utils.auth_required
async def update_project(request: Request, db: Session = Depends(common.get_db)):
    """更新項目資料"""
    user = manage_utils.get_system_user_from_header(request, db)
    data = await request.json()
    
    project_id = data.get('project_id', None)
    
    if not project_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 project_id 參數")
    
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        return common.standard_response(status="error", error_code=404, error_message="項目不存在")
    
    # 檢查權限 (只有 owner 或 admin 可以修改)
    if project.owner_id != user.user_id and user.role != 'admin':
        return common.standard_response(status="error", error_code=403, error_message="無權限修改此項目")
    
    # 更新字段
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    if 'workspace_path' in data:
        project.workspace_path = data['workspace_path']
    if 'tags' in data:
        project.tags = json.dumps(data['tags']) if isinstance(data['tags'], list) else data['tags']
    
    db.commit()
    db.refresh(project)
    
    return common.standard_response(response_data={"project": project.get_dict()})


@project_router.delete("/delete")
@manage_utils.auth_required
async def delete_project(request: Request, db: Session = Depends(common.get_db)):
    """刪除項目"""
    user = manage_utils.get_system_user_from_header(request, db)
    project_id = request.query_params.get('project_id', None)
    
    if not project_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 project_id 參數")
    
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        return common.standard_response(status="error", error_code=404, error_message="項目不存在")
    
    # 檢查權限 (只有 owner 或 admin 可以刪除)
    if project.owner_id != user.user_id and user.role != 'admin':
        return common.standard_response(status="error", error_code=403, error_message="無權限刪除此項目")
    
    # 執行 pre_delete hook (如果有)
    project.pre_delete(db)
    
    db.delete(project)
    db.commit()
    
    return common.standard_response(response_data={"message": "項目已刪除"})


@project_router.post("/assign-worker")
@manage_utils.auth_required
async def assign_worker_to_project(request: Request, db: Session = Depends(common.get_db)):
    """分配 Worker 比項目 (可考慮加中間表 project_workers)"""
    # TODO: 如果需要 many-to-many 關係，需要加 project_workers 表
    # 而家暂时返回 success，實際邏輯可以後面加
    data = await request.json()
    project_id = data.get('project_id')
    worker_id = data.get('worker_id')
    
    if not project_id or not worker_id:
        return common.standard_response(status="error", error_code=400, error_message="缺少 project_id 或 worker_id")
    
    # 驗證項目和 Worker 存在
    project = db.query(Project).filter(Project.project_id == project_id).first()
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    
    if not project or not worker:
        return common.standard_response(status="error", error_code=404, error_message="項目或 Worker 不存在")
    
    return common.standard_response(response_data={"message": "Worker 分配成功", "project_id": project_id, "worker_id": worker_id})
