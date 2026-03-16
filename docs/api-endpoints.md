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

## Project APIs (項目管理)

**Router:** `api/frontend/project.py`

### 1. 獲取項目列表

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

### 2. 獲取單一項目

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

### 3. 創建新項目

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

### 4. 更新項目

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

### 5. 刪除項目

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

### 6. 分配 Worker 比項目

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

## Auth APIs (認證)

**Router:** `api/frontend/auth.py`

### 登錄

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

---

## 文件位置

- **Project Router:** `api/frontend/project.py`
- **Auth Router:** `api/frontend/auth.py`
- **Common Utils:** `utils/common.py`, `utils/manage_utils.py`

---

*文檔更新日期: 2026-03-16*
