import requests
import config
import json
import time


# Webhook 方式呼叫 Agent
# 使用 /hooks/agent endpoint，唔會有 agent-to-agent announce 問題


def call_agent_async(message: str, agent_id: str, session_key: str, timeout: int = 120) -> dict:
    """
    透過 Webhooks 呼叫 Agent（異步，只返 runId）
    
    Args:
        message: Agent 要處理嘅訊息
        agent_id: Agent ID
        session_key: Session key (例如 "hook:worker:task-123")
        timeout: 逾時秒數 (default: 120)
    
    Returns:
        dict: { runId, status }
    """
    data = {
        "message": message,
        "sessionKey": session_key,
        "agentId": agent_id,
        "wakeMode": "now",
        "deliver": False,
        "timeoutSeconds": timeout,
    }
    
    headers = {
        "Authorization": f"Bearer {config.OPENCLAW_HOOKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"http://{config.OPENCLAW_HOST}{config.OPENCLAW_HOOKS_PATH}"
    response = requests.post(url, json=data, headers=headers, timeout=timeout + 10)
    return response.json()


def get_session_history(session_key: str, limit: int = 10) -> dict:
    """
    攞 session history
    
    Args:
        session_key: Session key
        limit: 攞幾多條 message
    
    Returns:
        dict: { messages: [...] }
    """
    data = {
        "tool": "sessions_history",
        "args": {
            "sessionKey": session_key,
            "limit": limit
        }
    }
    
    headers = {
        "Authorization": f"Bearer {config.OPENCLAW_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"http://{config.OPENCLAW_HOST}{config.OPENCLAW_SESSIONS_PATH}"
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def call_agent_sync(message: str, agent_id: str, session_key: str, timeout: int = 120, poll_interval: int = 2) -> dict:
    """
    透過 Webhooks 呼叫 Agent 並等待回覆（同步）
    
    流程:
    1. POST /hooks/agent → 返 runId
    2. Poll sessions_history 等待 agent 回覆
    3. 返 agent response
    
    Args:
        message: Agent 要處理嘅訊息
        agent_id: Agent ID
        session_key: Session key
        timeout: 逾時秒數
        poll_interval: Poll 間隔秒數
    
    Returns:
        dict: { status, reply, messages }
    """
    # 1. 觸發 webhook
    webhook_result = call_agent_async(message, agent_id, session_key, timeout)
    
    if webhook_result.get("status") not in ["accepted", "ok"]:
        return {
            "status": "error",
            "error": "Webhook failed",
            "details": webhook_result
        }
    
    run_id = webhook_result.get("runId")
    print(f"[Webhook] Triggered, runId: {run_id}")
    
    # 2. Poll session history
    start_time = time.time()
    last_message_count = 0
    
    while time.time() - start_time < timeout:
        time.sleep(poll_interval)
        
        history_result = get_session_history(session_key, limit=20)
        
        if history_result.get("ok") == False:
            # 可能 session 未創建，繼續 poll
            continue
        
        messages = history_result.get("result", {}).get("messages", [])
        
        # 檢查有冇新嘅 assistant message
        if len(messages) > last_message_count:
            # 搵最新嘅 assistant message
            for msg in reversed(messages):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    # 檢查係唔係已經完成（唔包含 "..." 等不完整標記）
                    if content and not content.endswith("..."):
                        return {
                            "status": "ok",
                            "runId": run_id,
                            "reply": content,
                            "messages": messages
                        }
            
            last_message_count = len(messages)
    
    return {
        "status": "timeout",
        "runId": run_id,
        "error": f"Agent did not respond within {timeout} seconds",
        "messages": get_session_history(session_key, limit=20).get("result", {}).get("messages", [])
    }


if __name__ == "__main__":
    # 測試呼叫 agent (同步)
    result = call_agent_sync(
        message="你好嗎?你係邊個?",
        agent_id="kevin",
        session_key="agent:kevin:man:test",
        timeout=120
    )
    
    print("=" * 50)
    print("Agent Response:")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))