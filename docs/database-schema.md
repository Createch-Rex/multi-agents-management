---
pdf_options:
  format: a4
  margin: 20mm
launch_options:
  args: ['--no-sandbox', '--disable-setuid-sandbox']
stylesheet: 'https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap'
css: |
  body { font-family: 'Noto Sans SC', sans-serif; }
  table { border-collapse: collapse; width: 100%; margin: 20px 0; }
  th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
  th { background-color: #f5f5f5; }
  code { background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
  pre { background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
---

# Database Schema

Multi-Agent Management System 既資料庫結構文檔。

## 概述

本系統使用 MySQL 資料庫，透過 SQLAlchemy ORM 進行操作。所有模型繼承自 `Base`，自動包含 `created_at` 同 `updated_at` 字段。

---

## 數據模型 (Models)

### 1. User (用戶)

**表名:** `user`

| 字段 | 類型 | 說明 |
|------|------|------|
| `user_id` | String(255) | 主鍵 (Primary Key) |
| `username` | String(255) | 用戶名 |
| `password` | Text | 密碼 (SHA256 加密) |
| `role` | String(50) | 角色 (admin/user) |
| `email` | String(255) | 電郵地址 (用於通知) |
| `created_at` | DateTime | 創建時間 (自動) |
| `updated_at` | DateTime | 更新時間 (自動) |

**關係:**
- 1:N → Project (通過 `owner_id`)

---

### 2. Project (項目)

**表名:** `project`

| 字段 | 類型 | 說明 |
|------|------|------|
| `project_id` | String(255) | 主鍵 |
| `name` | String(255) | 項目名稱 |
| `description` | Text | 項目描述 |
| `status` | String(255) | 項目狀態 |
| `workspace_path` | Text | 工作區路徑 |
| `owner_id` | String(255) | 外鍵 → `user.user_id` |
| `tags` | Text | JSON 数组 (分類標籤) |
| `created_at` | DateTime | 創建時間 (自動) |
| `updated_at` | DateTime | 更新時間 (自動) |

**關係:**
- N:1 → User (通過 `owner_id`)
- 1:N → Task

---

### 3. Task (任務)

**表名:** `task`

| 字段 | 類型 | 說明 |
|------|------|------|
| `task_id` | String(255) | 主鍵 |
| `project_id` | String(255) | 外鍵 → `project.project_id` |
| `title` | String(255) | 任務標題 |
| `description` | Text | 任務描述 |
| `worker_id` | String(255) | 外鍵 → `worker.worker_id` |
| `status` | String(255) | 任務狀態 |
| `chat_session` | String(255) | 聊天會話 ID |
| `priority` | String(50) | 優先級 (high/medium/low) |
| `due_date` | DateTime | 截止日期 |
| `parent_task_id` | String(255) | 外鍵 → `task.task_id` (任務依賴) |
| `created_at` | DateTime | 創建時間 (自動) |
| `updated_at` | DateTime | 更新時間 (自動) |

**關係:**
- N:1 → Project
- N:1 → Worker
- N:1 → Task (自引用，通過 `parent_task_id`)
- 1:N → Chat

---

### 4. Worker (工作者/Agent)

**表名:** `worker`

| 字段 | 類型 | 說明 |
|------|------|------|
| `worker_id` | String(255) | 主鍵 |
| `agent_id` | String(255) | Agent ID |
| `role` | String(255) | 角色 (CEO/Developer/QA 等) |
| `system_prompt` | Text | 系統提示詞 |
| `token` | String(255) | API Token |
| `heartbeat_interval` | Integer | 心跳間隔 (秒，默认 300) |
| `status` | String(50) | 狀態 (online/offline/busy) |
| `last_heartbeat` | DateTime | 最後心跳時間 |
| `capabilities` | Text | JSON 数组 (技能列表) |
| `max_concurrent_tasks` | Integer | 最大並發任務數 |
| `created_at` | DateTime | 創建時間 (自動) |
| `updated_at` | DateTime | 更新時間 (自動) |

**關係:**
- 1:N → Task

---

### 5. Chat (對話)

**表名:** `chat`

| 字段 | 類型 | 說明 |
|------|------|------|
| `chat_id` | String(255) | 主鍵 |
| `task_id` | String(255) | 外鍵 → `task.task_id` |
| `role` | String(255) | 角色標識 |
| `message` | Text | 對話內容 |
| `message_type` | String(50) | 消息類型 (user/agent/system) |
| `created_at` | DateTime | 創建時間 (自動) |
| `updated_at` | DateTime | 更新時間 (自動) |

**關係:**
- N:1 → Task

---

### 6. ProjectWorker (項目-工作者關聯表)

**表名:** `project_worker`

| 字段 | 類型 | 說明 |
|------|------|------|
| `project_id` | String(255) | 主鍵 + 外鍵 → `project.project_id` |
| `worker_id` | String(255) | 主鍵 + 外鍵 → `worker.worker_id` |
| `assigned_at` | DateTime | 分配時間 (默認: now) |
| `assigned_by` | String(255) | 外鍵 → `user.user_id` (分配者) |
| `status` | String(50) | 狀態 (active/inactive/removed, 默認: active) |

**關係:**
- N:1 → Project (通過 `project_id`)
- N:1 → Worker (通過 `worker_id`)
- N:1 → User (通過 `assigned_by`)

**說明:**
- 呢個係中間表 (junction table)，實現 Project 同 Worker 既 many-to-many 關係
- Composite Primary Key: `(project_id, worker_id)`
- 可以記錄邊個 (`assigned_by`) 喺幾時 (`assigned_at`) 分配咗個 Worker 比個 Project

---

## 實體關係圖 (ER Diagram)

```
┌─────────────┐
│    User     │
│  (用戶)     │
└──────┬──────┘
       │ 1:N
       │
       ▼
┌─────────────┐         ┌─────────────┐
│   Project   │────────▶│    Task     │
│  (項目)     │  1:N    │  (任務)     │
└──────┬──────┘         └──────┬──────┘
       │                      │ 1:N
       │ M:N                  │
       ▼                      ▼
┌─────────────┐         ┌─────────────┐
│ProjectWorker│◀────────│    Worker   │
│(關聯表)     │         │  (工作者)   │
└─────────────┘         └─────────────┘
                               │
                               │ 1:N (through Task)
                               │
                               ▼
                        ┌─────────────┐
                        │    Chat     │
                        │  (對話)     │
                        └─────────────┘
```

**Task 自引用關係:**
- `parent_task_id` → 任務依賴/子任務結構

---

## 自動字段 (Auto Fields)

所有模型繼承 `DBBase`，自動包含以下字段：

| 字段 | 類型 | 說明 |
|------|------|------|
| `created_at` | DateTime | 記錄創建時間 (default: now) |
| `updated_at` | DateTime | 記錄更新時間 (onupdate: now) |

---

## 文件位置

- **Models:** `database/models/*.py`
- **Database Config:** `database/database.py`
- **Base Class:** `database/db_base.py`

---

*文檔更新日期: 2026-03-16 (加咗 ProjectWorker model)*
