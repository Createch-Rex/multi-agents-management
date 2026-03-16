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
  .endpoint { background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #4CAF50; }
  .method-post { color: #2196F3; font-weight: bold; }
  .method-get { color: #4CAF50; font-weight: bold; }
  .method-put { color: #FF9800; font-weight: bold; }
  .method-delete { color: #F44336; font-weight: bold; }
---

# API Endpoints 文檔

Multi-Agent Management System 既 API 接口文檔。

## 概述

- **Base URL:** `/v1/api/frontend`
- **Auth:** 所有 endpoint 都需要 JWT Token (通過 `X-Auth-Token` header)
- **Response Format:** 統一使用 `standard_response` 格式

---

## Auth APIs (認證)

**Router:** `api/frontend/auth.py`

### 1. 登錄

**Endpoint:** `POST /auth/login`

**Method:** <span class="method-post">POST</span>

**Description:** 用戶登錄

**Request Body:**
```json
{
  "username": "user",
  "password": "pass123"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "token": "jwt_token_xxx",
    "user": {...}
  }
}
```

---

### 2. 註冊

**Endpoint:** `POST /auth/register`

**Method:** <span class="method-post">POST</span>

**Description:** 用戶註冊

**Request Body:**
```json
{
  "username": "newuser",
  "password": "pass123",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user": {...}
  }
}
```

---

### 3. 登出

**Endpoint:** `POST /auth/logout`

**Method:** <span class="method-post">POST</span>

**Description:** 用戶登出

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "登出成功"
  }
}
```

---

## Project APIs (項目管理)

**Router:** `api/frontend/project.py`

### 4. 獲取項目列表

**Endpoint:** `POST /project/list`

**Method:** <span class="method-post">POST</span>

**Description:** 獲取項目列表 (支持 pagination, search, filter)

**Request Body:**
```json
{
  "page": 1,
  "page_size": 20,
  "search_key": "keyword",
  "status": "active"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `page` | Integer | 否 | 頁碼 (默認: 1) |
| `page_size` | Integer | 否 | 每頁數量 (默認: 20) |
| `search_key` | String | 否 | 搜索關鍵字 (name/description) |
| `status` | String | 否 | 狀態過濾 |

**Response:**
```json
{
  "status": "success",
  "data": {
    "projects": [...],
    "total": 100
  }
}
```

**Features:**
- 普通用戶只睇到自己既項目
- Admin 睇所有項目
- 按 `created_at` 倒序 (最新既排頭)

---

### 5. 獲取單一項目

**Endpoint:** `GET /project/get`

**Method:** <span class="method-get">GET</span>

**Description:** 獲取單一項目詳情

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_id` | String | 是 | 項目 ID |

**Request Example:**
```
GET /project/get?project_id=xxx
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "project": {...}
  }
}
```

**Error Codes:**
- `400`: 缺少 project_id 參數
- `404`: 項目不存在

---

### 6. 創建新項目

**Endpoint:** `POST /project/create`

**Method:** <span class="method-post">POST</span>

**Description:** 創建新項目

**Request Body:**
```json
{
  "name": "項目名稱",
  "description": "項目描述",
  "status": "active",
  "workspace_path": "/path/to/workspace"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `name` | String | 是 | 項目名稱 |
| `description` | String | 否 | 項目描述 |
| `status` | String | 否 | 狀態 (默認: active) |
| `workspace_path` | String | 否 | 工作區路徑 |

**Response:**
```json
{
  "status": "success",
  "data": {
    "project": {...}
  }
}
```

**Error Codes:**
- `400`: 項目名稱不能为空

**自動字段:**
- `owner_id`: 自動設為當前用戶 ID
- `project_id`: 自動生成

---

### 7. 更新項目

**Endpoint:** `PUT /project/update`

**Method:** <span class="method-put">PUT</span>

**Description:** 更新項目資料

**Request Body:**
```json
{
  "project_id": "xxx",
  "name": "新名稱",
  "description": "新描述",
  "status": "completed",
  "workspace_path": "/new/path"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_id` | String | 是 | 項目 ID |
| `name` | String | 否 | 新名稱 |
| `description` | String | 否 | 新描述 |
| `status` | String | 否 | 新狀態 |
| `workspace_path` | String | 否 | 新路徑 |

**Response:**
```json
{
  "status": "success",
  "data": {
    "project": {...}
  }
}
```

**Error Codes:**
- `400`: 缺少 project_id 參數
- `404`: 項目不存在
- `403`: 無權限修改 (只有 owner 或 admin 可以)

---

### 8. 刪除項目

**Endpoint:** `DELETE /project/delete`

**Method:** <span class="method-delete">DELETE</span>

**Description:** 刪除項目

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_id` | String | 是 | 項目 ID |

**Request Example:**
```
DELETE /project/delete?project_id=xxx
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "項目已刪除"
  }
}
```

**Error Codes:**
- `400`: 缺少 project_id 參數
- `404`: 項目不存在
- `403`: 無權限刪除 (只有 owner 或 admin 可以)

**Hooks:**
- 調用 `project.pre_delete(db)` 進行清理

---

### 9. 分配 Worker 比項目

**Endpoint:** `POST /project/assign-worker`

**Method:** <span class="method-post">POST</span>

**Description:** 分配 Worker 比項目 (使用 project_worker 中間表)

**Request Body:**
```json
{
  "project_id": "xxx",
  "worker_id": "yyy"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_id` | String | 是 | 項目 ID |
| `worker_id` | String | 是 | Worker ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Worker 分配成功",
    "project_id": "xxx",
    "worker_id": "yyy",
    "assigned_at": "2026-03-16T14:00:00"
  }
}
```

**Error Codes:**
- `400`: 缺少 project_id 或 worker_id
- `404`: 項目或 Worker 不存在
- `409`: 呢個 Worker 已經分配咗比呢個項目 (重複 assignment)

**自動字段:**
- `assigned_by`: 自動設為當前用戶 ID
- `assigned_at`: 自動設為當前時間
- `status`: 默認 "active"

**表結構:**
- 使用 `project_worker` 中間表
- Composite Primary Key: `(project_id, worker_id)`

---

## Worker APIs (Worker 管理)

**Router:** `api/frontend/worker.py`

### 10. 獲取 Worker 列表

**Endpoint:** `POST /worker/list`

**Method:** <span class="method-post">POST</span>

**Description:** 獲取 Worker 列表 (支持 pagination, search)

**Request Body:**
```json
{
  "page": 1,
  "page_size": 20,
  "search_key": "keyword"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "workers": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 11. 獲取單一 Worker

**Endpoint:** `GET /worker/get`

**Method:** <span class="method-get">GET</span>

**Description:** 獲取單一 Worker 詳情

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `worker_id` | String | 是 | Worker ID |

---

### 12. 創建 Worker

**Endpoint:** `POST /worker/create`

**Method:** <span class="method-post">POST</span>

**Description:** 創建新 Worker

**Request Body:**
```json
{
  "name": "Worker 名稱",
  "description": "描述",
  "config": {}
}
```

---

### 13. 更新 Worker

**Endpoint:** `PUT /worker/update`

**Method:** <span class="method-put">PUT</span>

**Description:** 更新 Worker 資料

**Request Body:**
```json
{
  "worker_id": "xxx",
  "name": "新名稱",
  "description": "新描述",
  "config": {}
}
```

---

### 14. 刪除 Worker

**Endpoint:** `DELETE /worker/delete`

**Method:** <span class="method-delete">DELETE</span>

**Description:** 刪除 Worker

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `worker_id` | String | 是 | Worker ID |

---

## User APIs (用戶管理)

**Router:** `api/frontend/user.py`

### 15. 獲取用戶列表

**Endpoint:** `POST /user/list`

**Method:** <span class="method-post">POST</span>

**Description:** 獲取用戶列表 (只有 admin 可用, 支持 pagination, search, role filter)

**Request Body:**
```json
{
  "page": 1,
  "page_size": 20,
  "search_key": "keyword",
  "role": "user"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "users": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**權限:** 只有 admin 可以查看用戶列表

---

### 16. 獲取單一用戶

**Endpoint:** `GET /user/get`

**Method:** <span class="method-get">GET</span>

**Description:** 獲取單一用戶詳情

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `user_id` | String | 是 | 用戶 ID |

**權限:** 普通用戶只能查看自己

---

### 17. 創建用戶

**Endpoint:** `POST /user/create`

**Method:** <span class="method-post">POST</span>

**Description:** 創建新用戶 (只有 admin 可以)

**Request Body:**
```json
{
  "username": "newuser",
  "password": "pass123",
  "role": "user",
  "email": "user@example.com"
}
```

**權限:** 只有 admin 可以創建用戶

---

### 18. 更新用戶

**Endpoint:** `PUT /user/update`

**Method:** <span class="method-put">PUT</span>

**Description:** 更新用戶資料

**Request Body:**
```json
{
  "user_id": "xxx",
  "username": "新用戶名",
  "email": "新email",
  "role": "admin",
  "password": "新密碼"
}
```

**權限:**
- 只有 admin 可以改 username 和 role
- 其他用戶可以改自己既 email 和密碼

---

### 19. 刪除用戶

**Endpoint:** `DELETE /user/delete`

**Method:** <span class="method-delete">DELETE</span>

**Description:** 刪除用戶 (只有 admin 可以)

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `user_id` | String | 是 | 用戶 ID |

**Error Codes:**
- `400`: 唔可以刪除自己
- `409`: 用戶仲有項目或 Worker 分配記錄

---

## Chat APIs (對話管理)

**Router:** `api/frontend/chat.py`

### 20. 獲取 Chat 列表

**Endpoint:** `POST /chat/list`

**Method:** <span class="method-post">POST</span>

**Description:** 獲取 Chat 列表 (按 task_id 過濾, 支持 pagination, search)

**Request Body:**
```json
{
  "task_id": "xxx",
  "page": 1,
  "page_size": 50,
  "search_key": "keyword"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `task_id` | String | 是 | Task ID |
| `page` | Integer | 否 | 頁碼 (默認: 1) |
| `page_size` | Integer | 否 | 每頁數量 (默認: 50) |
| `search_key` | String | 否 | 搜索關鍵字 (message 內容) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "chats": [
      {
        "chat_id": "xxx",
        "task_id": "xxx",
        "role": "user",
        "message": "Hello",
        "message_type": "user",
        "created_at": "2026-03-16T14:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 50
  }
}
```

**Features:**
- 按 `created_at` 升序 (舊既係前面)
- 返回既 message 係實際既對話內容

---

### 21. 創建 Chat 訊息

**Endpoint:** `POST /chat/create`

**Method:** <span class="method-post">POST</span>

**Description:** 創建新 Chat 訊息

**Request Body:**
```json
{
  "task_id": "xxx",
  "role": "user",
  "message": "Hello World",
  "message_type": "user"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `task_id` | String | 是 | Task ID |
| `role` | String | 否 | 角色 (默認: user) |
| `message` | String | 是 | 訊息內容 |
| `message_type` | String | 否 | 訊息類型 (默認: user) |

**Valid Values:**
- `role`: `user`, `agent`, `system`
- `message_type`: `user`, `agent`, `system`

**Response:**
```json
{
  "status": "success",
  "data": {
    "chat": {...}
  }
}
```

**Error Codes:**
- `400`: 缺少 task_id 或 message
- `404`: Task 不存在

---

### 22. 更新 Chat 訊息

**Endpoint:** `PUT /chat/update`

**Method:** <span class="method-put">PUT</span>

**Description:** 更新 Chat 訊息

**Request Body:**
```json
{
  "chat_id": "xxx",
  "message": "更新後既訊息",
  "message_type": "agent"
}
```

**Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `chat_id` | String | 是 | Chat ID |
| `message` | String | 否 | 新訊息內容 |
| `message_type` | String | 否 | 新訊息類型 |

**Response:**
```json
{
  "status": "success",
  "data": {
    "chat": {...}
  }
}
```

**Error Codes:**
- `400`: 缺少 chat_id
- `404`: Chat 不存在

---

### 23. 刪除 Chat 訊息

**Endpoint:** `DELETE /chat/delete`

**Method:** <span class="method-delete">DELETE</span>

**Description:** 刪除 Chat 訊息

**Query Parameters:**
| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `chat_id` | String | 是 | Chat ID |

**Request Example:**
```
DELETE /chat/delete?chat_id=xxx
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Chat 已刪除"
  }
}
```

**Error Codes:**
- `400`: 缺少 chat_id
- `404`: Chat 不存在

---

## 通用 Response 格式

所有 API 使用 `standard_response` 統一格式：

**Success:**
```json
{
  "status": "success",
  "data": {...}
}
```

**Error:**
```json
{
  "status": "error",
  "error_code": 400,
  "error_message": "錯誤描述"
}
```

---

## 權限說明

| 操作 | 普通用戶 | Admin |
|------|----------|-------|
| 查看自己項目 | ✅ | ✅ |
| 查看所有項目 | ❌ | ✅ |
| 創建項目 | ✅ | ✅ |
| 修改自己項目 | ✅ | ✅ |
| 修改他人項目 | ❌ | ✅ |
| 刪除自己項目 | ✅ | ✅ |
| 刪除他人項目 | ❌ | ✅ |
| 分配 Worker | ✅ | ✅ |
| 查看用戶列表 | ❌ | ✅ |
| 創建用戶 | ❌ | ✅ |
| 刪除用戶 | ❌ | ✅ |

---

## 文件位置

- **Auth Router:** `api/frontend/auth.py`
- **Project Router:** `api/frontend/project.py`
- **Worker Router:** `api/frontend/worker.py`
- **User Router:** `api/frontend/user.py`
- **Chat Router:** `api/frontend/chat.py`
- **Common Utils:** `utils/common.py`, `utils/manage_utils.py`

---

*文檔更新日期: 2026-03-16*