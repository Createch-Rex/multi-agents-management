#!/usr/bin/env python3
"""
Demo data seeder for multi-agents-management
Run: python seed_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, engine, Base
from database.models.user import User
from database.models.project import Project
from database.models.worker import Worker
from database.models.task import Task
from database.models.project_worker import ProjectWorker
from database.models.chat import Chat
import hashlib
from datetime import datetime, timedelta
import uuid

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_demo_data():
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if demo data already exists
        existing = db.query(Project).filter(Project.name.like('Demo%')).first()
        if existing:
            print("Demo data already exists! Skipping...")
            return
        
        # ==================== USERS ====================
        admin_user = User(
            user_id="user_admin",
            username="admin",
            password=hash_password("admin123"),
            role="admin",
            email="admin@example.com"
        )
        
        dev_user = User(
            user_id="user_dev",
            username="developer",
            password=hash_password("dev123"),
            role="user",
            email="dev@example.com"
        )
        
        db.add_all([admin_user, dev_user])
        db.commit()
        print("✓ Users created")
        
        # ==================== PROJECTS ====================
        projects = [
            Project(
                project_id="proj_demo_1",
                name="Demo 教育中心系統",
                description="教育中心管理系統，包括學生管理、課程安排、成績管理等模塊",
                status="running",
                workspace_path="/workspace/projects/education_system",
                owner_id="user_admin",
                amount=150000.0
            ),
            Project(
                project_id="proj_demo_2",
                name="Demo 補習中心系統",
                description="補習中心預約系統，支援網上預約、繳費、管理後台",
                status="running",
                workspace_path="/workspace/projects/tutorial_center",
                owner_id="user_admin",
                amount=80000.0
            ),
            Project(
                project_id="proj_demo_3",
                name="Demo 足球分析系統",
                description="足球比賽分析系統，包含數據收集、模型訓練、預測展示",
                status="planning",
                workspace_path="/workspace/projects/football_analysis",
                owner_id="user_dev",
                amount=120000.0
            ),
        ]
        
        db.add_all(projects)
        db.commit()
        print("✓ Projects created")
        
        # ==================== WORKERS ====================
        workers = [
            Worker(
                worker_id="worker_1",
                agent_id="agent_coder_01",
                role="coder",
                system_prompt="你是一個專業的Python開發者，負責編寫高質量代碼。",
                token=str(uuid.uuid4()),
                heartbeat_interval=300,
                status="online",
                last_heartbeat=datetime.now(),
                capabilities='["python", "javascript", "react", "nodejs"]',
                max_concurrent_tasks=2
            ),
            Worker(
                worker_id="worker_2",
                agent_id="agent_analyst_01",
                role="analyst",
                system_prompt="你是一個數據分析專家，負責分析和可視化數據。",
                token=str(uuid.uuid4()),
                heartbeat_interval=300,
                status="online",
                last_heartbeat=datetime.now(),
                capabilities='["data_analysis", "visualization", "sql"]',
                max_concurrent_tasks=1
            ),
            Worker(
                worker_id="worker_3",
                agent_id="agent_researcher_01",
                role="researcher",
                system_prompt="你是一個研究助理，負責搜集和整理資訊。",
                token=str(uuid.uuid4()),
                heartbeat_interval=300,
                status="offline",
                last_heartbeat=datetime.now() - timedelta(hours=2),
                capabilities='["research", "writing", "web_search"]',
                max_concurrent_tasks=3
            ),
        ]
        
        db.add_all(workers)
        db.commit()
        print("✓ Workers created")
        
        # ==================== TASKS ====================
        tasks = [
            # Project 1 tasks
            Task(
                task_id="task_1",
                project_id="proj_demo_1",
                title="設計數據庫結構",
                description="為教育中心系統設計學生表、課程表、成績表",
                worker_id="worker_1",
                status="completed",
                chat_session=str(uuid.uuid4()),
                priority="high",
                due_date=datetime.now() + timedelta(days=7)
            ),
            Task(
                task_id="task_2",
                project_id="proj_demo_1",
                title="開發學生管理模塊",
                description="實現學生的增刪改查功能",
                worker_id="worker_1",
                status="ongoing",
                chat_session=str(uuid.uuid4()),
                priority="high",
                due_date=datetime.now() + timedelta(days=14)
            ),
            Task(
                task_id="task_3",
                project_id="proj_demo_1",
                title="開發課程安排功能",
                description="實現課程時間表和教師分配",
                worker_id="worker_2",
                status="ongoing",
                chat_session=str(uuid.uuid4()),
                priority="medium",
                due_date=datetime.now() + timedelta(days=21)
            ),
            # Project 2 tasks
            Task(
                task_id="task_4",
                project_id="proj_demo_2",
                title="設計預約流程",
                description="設計補習中心預約系統的用戶流程",
                worker_id="worker_3",
                status="completed",
                chat_session=str(uuid.uuid4()),
                priority="high",
                due_date=datetime.now() + timedelta(days=5)
            ),
            Task(
                task_id="task_5",
                project_id="proj_demo_2",
                title="開發預約API",
                description="實現預約相關的RESTful API",
                worker_id="worker_1",
                status="ongoing",
                chat_session=str(uuid.uuid4()),
                priority="medium",
                due_date=datetime.now() + timedelta(days=10)
            ),
            # Project 3 tasks
            Task(
                task_id="task_6",
                project_id="proj_demo_3",
                title="收集足球數據",
                description="從API收集五大聯賽的比賽數據",
                worker_id="worker_3",
                status="ongoing",
                chat_session=str(uuid.uuid4()),
                priority="medium",
                due_date=datetime.now() + timedelta(days=30)
            ),
        ]
        
        db.add_all(tasks)
        db.commit()
        print("✓ Tasks created")
        
        # ==================== PROJECT-WORKER ASSIGNMENTS ====================
        assignments = [
            ProjectWorker(
                project_id="proj_demo_1",
                worker_id="worker_1",
                assigned_at=datetime.now(),
                assigned_by="user_admin",
                status="active"
            ),
            ProjectWorker(
                project_id="proj_demo_1",
                worker_id="worker_2",
                assigned_at=datetime.now(),
                assigned_by="user_admin",
                status="active"
            ),
            ProjectWorker(
                project_id="proj_demo_2",
                worker_id="worker_1",
                assigned_at=datetime.now(),
                assigned_by="user_admin",
                status="active"
            ),
            ProjectWorker(
                project_id="proj_demo_2",
                worker_id="worker_3",
                assigned_at=datetime.now(),
                assigned_by="user_admin",
                status="active"
            ),
            ProjectWorker(
                project_id="proj_demo_3",
                worker_id="worker_2",
                assigned_at=datetime.now(),
                assigned_by="user_dev",
                status="active"
            ),
            ProjectWorker(
                project_id="proj_demo_3",
                worker_id="worker_3",
                assigned_at=datetime.now(),
                assigned_by="user_dev",
                status="active"
            ),
        ]
        
        db.add_all(assignments)
        db.commit()
        print("✓ Project-Worker assignments created")
        
        # ==================== CHAT MESSAGES ====================
        chats = [
            Chat(
                chat_id=str(uuid.uuid4()),
                task_id="task_1",
                role="user",
                message="請幫我設計教育中心系統的數據庫結構",
                message_type="user"
            ),
            Chat(
                chat_id=str(uuid.uuid4()),
                task_id="task_1",
                role="agent",
                message="好的，我來為你設計一個完整的數據庫結構。學生表需要包含姓名、年齡、聯繫方式等字段...",
                message_type="agent"
            ),
            Chat(
                chat_id=str(uuid.uuid4()),
                task_id="task_2",
                role="user",
                message="請開發學生管理模塊的CRUD功能",
                message_type="user"
            ),
            Chat(
                chat_id=str(uuid.uuid4()),
                task_id="task_2",
                role="agent",
                message="收到！我會使用Python + Flask + MySQL來實現這個模塊",
                message_type="agent"
            ),
        ]
        
        db.add_all(chats)
        db.commit()
        print("✓ Chat messages created")
        
        print("\n" + "="*50)
        print("Demo data seeded successfully!")
        print("="*50)
        print("\nDemo Users:")
        print("  - admin / admin123 (admin role)")
        print("  - developer / dev123 (user role)")
        print("\nDemo Projects:")
        print("  - Demo 教育中心系統 (running)")
        print("  - Demo 補習中心系統 (running)")
        print("  - Demo 足球分析系統 (planning)")
        print("\nDemo Workers:")
        print("  - worker_1 (coder, online)")
        print("  - worker_2 (analyst, online)")
        print("  - worker_3 (researcher, offline)")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
