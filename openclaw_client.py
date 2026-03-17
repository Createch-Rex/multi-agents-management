"""
OpenClaw Webhook Client

提供所有 OpenClaw Webhook API 嘅 Python function 封裝

Endpoints:
- POST /hooks/wake      - 觸發 main session heartbeat
- POST /hooks/agent     - 觸發 isolated agent run
- POST /hooks/<name>    - 自定義 mapping (需要 config)
- POST /tools/invoke    - 調用 tool (sessions_history 等)
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class OpenClawConfig:
    """OpenClaw 配置"""
    host: str
    hooks_token: str
    gateway_token: str
    hooks_path: str = "/hooks"
    tools_path: str = "/tools/invoke"
    timeout: int = 120


class OpenClawClient:
    """OpenClaw Webhook Client"""
    
    def __init__(self, config: OpenClawConfig):
        self.config = config
        self.base_url = f"http://{config.host}"
    
    # ==================== WEBHOOK ENDPOINTS ====================
    
    def wake(
        self,
        text: str,
        mode: str = "now"
    ) -> Dict[str, Any]:
        """
        POST /hooks/wake - 觸發 main session heartbeat
        
        Args:
            text: 事件描述 (e.g., "New email received")
            mode: "now" (即時) 或 "next-heartbeat" (等下一次)
        
        Returns:
            dict: { status, ... }
        
        Example:
            client.wake("New email received", mode="now")
        """
        data = {
            "text": text,
            "mode": mode
        }
        
        headers = self._get_hooks_headers()
        url = f"{self.base_url}{self.config.hooks_path}/wake"
        
        response = requests.post(url, json=data, headers=headers, timeout=self.config.timeout)
        return response.json()
    
    def call_agent(
        self,
        message: str,
        name: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_key: Optional[str] = None,
        wake_mode: str = "now",
        deliver: bool = False,
        channel: Optional[str] = None,
        to: Optional[str] = None,
        model: Optional[str] = None,
        thinking: Optional[str] = None,
        timeout_seconds: int = 120
    ) -> Dict[str, Any]:
        """
        POST /hooks/agent - 觸發 isolated agent run
        
        Args:
            message: Agent 要處理嘅訊息 (必填)
            name: Human-readable name for hook (e.g., "GitHub")
            agent_id: 指定 agent ID
            session_key: Session key (需要 allowRequestSessionKey: true)
            wake_mode: "now" (即時) 或 "next-heartbeat"
            deliver: 是否 send 去 messaging channel (default: False)
            channel: messaging channel ("last", "whatsapp", "telegram", etc.)
            to: 收件人 ID
            model: Model override (e.g., "openai/gpt-5.2-mini")
            thinking: Thinking level ("low", "medium", "high")
            timeout_seconds: 逾時秒數
        
        Returns:
            dict: { runId, status: "accepted" }
        
        Example:
            # 基本呼叫
            client.call_agent("Summarize inbox")
            
            # 指定 agent
            client.call_agent("你的任務", agent_id="worker")
            
            # 指定 session (需要 config enable)
            client.call_agent("你的任務", session_key="hook:worker:task-123")
        """
        data = {
            "message": message,
            "wakeMode": wake_mode,
            "timeoutSeconds": timeout_seconds
        }
        
        # 可選參數
        if name:
            data["name"] = name
        if agent_id:
            data["agentId"] = agent_id
        if session_key:
            data["sessionKey"] = session_key
        if deliver is not None:
            data["deliver"] = deliver
        if channel:
            data["channel"] = channel
        if to:
            data["to"] = to
        if model:
            data["model"] = model
        if thinking:
            data["thinking"] = thinking
        
        headers = self._get_hooks_headers()
        url = f"{self.base_url}{self.config.hooks_path}/agent"
        
        response = requests.post(url, json=data, headers=headers, timeout=timeout_seconds + 10)
        return response.json()
    
    def call_mapped_hook(
        self,
        hook_name: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        POST /hooks/<name> - 調用自定義 mapping hook
        
        Args:
            hook_name: Hook name (需要在 hooks.mappings 配置)
            payload: 自定義 payload
        
        Returns:
            dict: Response
        
        Example:
            client.call_mapped_hook("gmail", {
                "source": "gmail",
                "messages": [{"from": "Ada", "subject": "Hello"}]
            })
        """
        headers = self._get_hooks_headers()
        url = f"{self.base_url}{self.config.hooks_path}/{hook_name}"
        
        response = requests.post(url, json=payload, headers=headers, timeout=self.config.timeout)
        return response.json()
    
    # ==================== TOOLS INVOKE ====================
    
    def invoke_tool(
        self,
        tool: str,
        args: Optional[Dict[str, Any]] = None,
        session_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        POST /tools/invoke - 調用 OpenClaw tool
        
        Args:
            tool: Tool name (e.g., "sessions_list", "sessions_history")
            args: Tool arguments
            session_key: Target session key
        
        Returns:
            dict: { ok, result } or { ok: false, error }
        
        Example:
            client.invoke_tool("sessions_list", {"limit": 10})
            client.invoke_tool("sessions_history", {"sessionKey": "main", "limit": 20})
        """
        data = {
            "tool": tool
        }
        
        if args:
            data["args"] = args
        if session_key:
            data["sessionKey"] = session_key
        
        headers = self._get_gateway_headers()
        url = f"{self.base_url}{self.config.tools_path}"
        
        response = requests.post(url, json=data, headers=headers, timeout=self.config.timeout)
        return response.json()
    
    # ==================== SESSION HELPERS ====================
    
    def get_session_history(
        self,
        session_key: str,
        limit: int = 20,
        include_tools: bool = False
    ) -> Dict[str, Any]:
        """
        攞 session 歷史訊息
        
        Args:
            session_key: Session key
            limit: 攞幾多條 message
            include_tools: 是否包含 tool messages
        
        Returns:
            dict: { ok, result: { messages: [...] } }
        """
        return self.invoke_tool("sessions_history", {
            "sessionKey": session_key,
            "limit": limit,
            "includeTools": include_tools
        })
    
    def list_sessions(
        self,
        kinds: Optional[List[str]] = None,
        limit: int = 50,
        active_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        列出 sessions
        
        Args:
            kinds: Session types ("main", "group", "cron", "hook", "node", "other")
            limit: Max rows
            active_minutes: 只列出 N 分鐘內活躍嘅 sessions
        
        Returns:
            dict: { ok, result: [...] }
        """
        args = {"limit": limit}
        if kinds:
            args["kinds"] = kinds
        if active_minutes:
            args["activeMinutes"] = active_minutes
        
        return self.invoke_tool("sessions_list", args)
    
    # ==================== SYNC CALL (POLLING) ====================
    
    def call_agent_sync(
        self,
        message: str,
        agent_id: Optional[str] = None,
        session_key: str = "hook:default",
        timeout: int = 120,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """
        同步呼叫 Agent (poll session history 等待回覆)
        
        流程:
        1. POST /hooks/agent → { runId }
        2. Poll sessions_history 等待 agent 回覆
        3. 返 agent response
        
        Args:
            message: Agent 要處理嘅訊息
            agent_id: Agent ID
            session_key: Session key
            timeout: 逾時秒數
            poll_interval: Poll 間隔秒數
        
        Returns:
            dict: { status, runId, reply, messages }
        """
        # 1. 觸發 webhook
        webhook_result = self.call_agent(
            message=message,
            agent_id=agent_id,
            session_key=session_key,
            timeout_seconds=timeout
        )
        
        if webhook_result.get("status") not in ["accepted", "ok"]:
            return {
                "status": "error",
                "error": "Webhook failed",
                "details": webhook_result
            }
        
        run_id = webhook_result.get("runId")
        
        # 2. Poll session history
        start_time = time.time()
        last_message_count = 0
        
        while time.time() - start_time < timeout:
            time.sleep(poll_interval)
            
            history_result = self.get_session_history(session_key, limit=20)
            
            if not history_result.get("ok"):
                continue
            
            messages = history_result.get("result", {}).get("messages", [])
            
            # 檢查有冇新嘅 assistant message
            if len(messages) > last_message_count:
                for msg in reversed(messages):
                    if msg.get("role") == "assistant":
                        content = msg.get("content", "")
                        # 檢查完成（唔包含 "..." 等不完整標記）
                        if content and not content.endswith("..."):
                            return {
                                "status": "ok",
                                "runId": run_id,
                                "reply": content,
                                "messages": messages
                            }
                
                last_message_count = len(messages)
        
        # Timeout
        final_history = self.get_session_history(session_key, limit=20)
        return {
            "status": "timeout",
            "runId": run_id,
            "error": f"Agent did not respond within {timeout} seconds",
            "messages": final_history.get("result", {}).get("messages", [])
        }
    
    # ==================== PRIVATE HELPERS ====================
    
    def _get_hooks_headers(self) -> Dict[str, str]:
        """Get headers for hooks endpoints"""
        return {
            "Authorization": f"Bearer {self.config.hooks_token}",
            "Content-Type": "application/json"
        }
    
    def _get_gateway_headers(self) -> Dict[str, str]:
        """Get headers for gateway endpoints"""
        return {
            "Authorization": f"Bearer {self.config.gateway_token}",
            "Content-Type": "application/json"
        }


# ==================== FACTORY FUNCTION ====================

def create_client(
    host: str,
    hooks_token: str,
    gateway_token: str,
    timeout: int = 120
) -> OpenClawClient:
    """
    建立 OpenClaw Client
    
    Args:
        host: OpenClaw host (e.g., "10.18.0.24:18789")
        hooks_token: Hooks token (for /hooks/* endpoints)
        gateway_token: Gateway token (for /tools/invoke)
        timeout: Default timeout in seconds
    
    Returns:
        OpenClawClient instance
    """
    config = OpenClawConfig(
        host=host,
        hooks_token=hooks_token,
        gateway_token=gateway_token,
        timeout=timeout
    )
    return OpenClawClient(config)


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # 範例
    client = create_client(
        host="10.18.0.24:18789",
        hooks_token="shared-secret",
        gateway_token="your-gateway-token"
    )
    
    # 1. Wake main session
    result = client.wake("System check")
    print(f"Wake result: {result}")
    
    # 2. Call agent (async)
    result = client.call_agent(
        message="Hello, who are you?",
        agent_id="main",
        deliver=False
    )
    print(f"Agent triggered: {result}")
    
    # 3. Call agent (sync, wait for response)
    result = client.call_agent_sync(
        message="Summarize today's tasks",
        agent_id="main",
        session_key="hook:worker:test",
        timeout=120
    )
    print(f"Agent response: {result}")
    
    # 4. List sessions
    result = client.list_sessions(limit=10)
    print(f"Sessions: {json.dumps(result, indent=2)}")
    
    # 5. Get session history
    result = client.get_session_history("main", limit=10)
    print(f"History: {json.dumps(result, indent=2)}")