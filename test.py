import requests
import config
import json


# Webhook 方式呼叫 Agent
# 使用 /hooks/agent endpoint，唔會有 agent-to-agent announce 問題


def call_agent_with_session(message: str, agent_id: str, session_key: str, timeout: int = 120) -> dict:
    """
    透過 Webhooks 呼叫 Agent（指定 session key）
    
    注意：需要 config 中設定 allowRequestSessionKey: true
    
    Args:
        message: Agent 要處理嘅訊息
        agent_id: Agent ID
        session_key: Session key (例如 "hook:worker:task-123")
        timeout: 逾時秒數 (default: 120)
    
    Returns:
        dict: Agent 回覆結果
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
    print(response.content)
    return response.json()


if __name__ == "__main__":
    # 測試呼叫 agent
    result = call_agent_with_session("你好嗎?你係邊個?", agent_id="kevin", session_key="agent:kevin:man:test")
    
    print("=" * 50)
    print("Webhook Response:")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))