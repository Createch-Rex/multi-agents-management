# Worker Available Endpoints

Base URL: `/v1/api/worker`

所有 endpoints 都必須在 Header 中包含 token：
```
X-Worker-Token: YOUR_TOKEN_HERE
```

---

## Endpoints List

### Auth
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/worker/auth/activate` | GET | (public, need agent_id) |

### Self
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/worker/self` | GET | - |
| `/worker/self/update` | PUT | `update_self` |

### Workers
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/workers` | GET | `list_workers` |
| `/workers/{id}` | GET | `view_worker` |

### Endpoints
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/worker/endpoints` | GET | - |

### Tasks
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/task/list` | GET | `list_tasks` |
| `/task/{id}` | GET | `view_task` |
| `/task/create` | POST | `create_task` |
| `/task/{id}/update` | PUT | `update_task` |
| `/task/{id}/progress` | GET | `track_progress` |
| `/task/{id}/assign` | POST | `assign_task` |

### Projects
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/project/list` | GET | `list_projects` |
| `/project/{id}` | GET | `view_project` |

### Chat
| Endpoint | Method | Required Capability |
|----------|--------|---------------------|
| `/chat/list` | POST | `view_chat` |
| `/chat/create` | POST | `create_chat` |

---

## Default Capabilities by Role

### CEO
- `list_workers`
- `view_worker`
- `list_tasks`
- `view_task`
- `create_task`
- `update_task`
- `track_progress`
- `assign_task`
- `list_projects`
- `view_project`
- `view_chat`
- `create_chat`
- `update_self`

### Developer
- `list_tasks`
- `view_task`
- `update_task`
- `list_projects`
- `view_project`
- `view_chat`
- `create_chat`
- `update_self`

### Designer
- `list_tasks`
- `view_task`
- `update_task`
- `list_projects`
- `view_project`
- `view_chat`
- `create_chat`
- `update_self`