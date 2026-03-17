"""
OpenClaw Webhook Client

提供 OpenClaw Webhook API 同 tools invoke 嘅 Python 封裝。

Endpoints:
- POST /hooks/wake      - 觸發 main session heartbeat
- POST /hooks/agent     - 觸發 isolated agent run
- POST /hooks/<name>    - 調用自定義 mapped hook
- POST /tools/invoke    - 調用 tool (sessions_list / sessions_history 等)
"""

import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import requests


@dataclass
class OpenClawConfig:
    """OpenClaw 配置"""
    host: str
    hooks_token: str
    gateway_token: str
    hooks_path: str = "/hooks"
    tools_path: str = "/tools/invoke"
    timeout: int = 30


class OpenClawClient:
    """OpenClaw Webhook Client"""

    def __init__(self, config: OpenClawConfig):
        self.config = config
        self.base_url = f"http://{config.host}" if not str(config.host).startswith(("http://", "https://")) else str(config.host).rstrip("/")

    # ==================== WEBHOOK ENDPOINTS ====================

    def wake(
        self,
        text: str,
        mode: str = "now"
    ) -> Dict[str, Any]:
        """
        POST /hooks/wake - 觸發 main session heartbeat
        """
        data = {
            "text": text,
            "mode": mode
        }
        return self._post_json(
            path=f"{self.config.hooks_path}/wake",
            payload=data,
            headers=self._get_hooks_headers(),
            timeout=self.config.timeout,
        )

    def call_agent(
        self,
        message: str,
        name: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_key: Optional[str] = None,
        wake_mode: str = "now",
        deliver: Optional[bool] = None,
        channel: Optional[str] = None,
        to: Optional[str] = None,
        model: Optional[str] = None,
        thinking: Optional[str] = None,
        timeout_seconds: int = 120,
        request_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        POST /hooks/agent - 觸發 isolated agent run

        注意：
        - OpenClaw docs 指出 deliver 預設係 true，所以唔想送出訊息要明確傳 deliver=False
        - sessionKey 只有在 hooks.allowRequestSessionKey=true 時先可由 request 指定
        """
        data = {
            "message": message,
            "wakeMode": wake_mode,
            "timeoutSeconds": timeout_seconds,
        }

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

        return self._post_json(
            path=f"{self.config.hooks_path}/agent",
            payload=data,
            headers=self._get_hooks_headers(),
            timeout=request_timeout or self.config.timeout,
        )

    def call_mapped_hook(
        self,
        hook_name: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        POST /hooks/<name> - 調用自定義 mapping hook
        """
        return self._post_json(
            path=f"{self.config.hooks_path}/{hook_name}",
            payload=payload,
            headers=self._get_hooks_headers(),
            timeout=self.config.timeout,
        )

    # ==================== TOOLS INVOKE ====================

    def invoke_tool(
        self,
        tool: str,
        args: Optional[Dict[str, Any]] = None,
        session_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /tools/invoke - 調用 OpenClaw tool
        """
        data: Dict[str, Any] = {"tool": tool}
        if args:
            data["args"] = args
        if session_key:
            data["sessionKey"] = session_key

        return self._post_json(
            path=self.config.tools_path,
            payload=data,
            headers=self._get_gateway_headers(),
            timeout=self.config.timeout,
        )

    # ==================== SESSION HELPERS ====================

    def get_session_history(
        self,
        session_key: str,
        limit: int = 20,
        include_tools: bool = False,
    ) -> Dict[str, Any]:
        return self.invoke_tool("sessions_history", {
            "sessionKey": session_key,
            "limit": limit,
            "includeTools": include_tools,
        })

    def list_sessions(
        self,
        kinds: Optional[List[str]] = None,
        limit: int = 50,
        active_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        args: Dict[str, Any] = {"limit": limit}
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
        poll_interval: int = 2,
        name: Optional[str] = None,
        wake_mode: str = "now",
        deliver: Optional[bool] = False,
        channel: Optional[str] = None,
        to: Optional[str] = None,
        model: Optional[str] = None,
        thinking: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        同步呼叫 Agent (先 webhook，再 poll sessions_history 等回覆)

        做法：
        1. 先取一次 session history 做 baseline
        2. call /hooks/agent
        3. 只接受 baseline 之後新增嘅 assistant message
        """
        baseline_result = self.get_session_history(session_key, limit=100)
        baseline_messages = self._extract_messages(baseline_result)
        baseline_ids = self._collect_message_ids(baseline_messages)
        baseline_len = len(baseline_messages)

        webhook_result = self.call_agent(
            message=message,
            name=name,
            agent_id=agent_id,
            session_key=session_key,
            wake_mode=wake_mode,
            deliver=deliver,
            channel=channel,
            to=to,
            model=model,
            thinking=thinking,
            timeout_seconds=timeout,
            request_timeout=min(self.config.timeout, timeout),
        )

        if webhook_result.get("status") not in ["accepted", "ok"]:
            return {
                "status": "error",
                "error": "Webhook failed",
                "details": webhook_result,
            }

        run_id = webhook_result.get("runId")
        start_time = time.time()

        while time.time() - start_time < timeout:
            time.sleep(poll_interval)
            history_result = self.get_session_history(session_key, limit=100)

            if not history_result.get("ok"):
                continue

            messages = self._extract_messages(history_result)
            new_messages = self._filter_new_messages(messages, baseline_ids, baseline_len)
            assistant_messages = [msg for msg in new_messages if self._message_role(msg) == "assistant" and self._message_content(msg).strip()]

            if assistant_messages:
                latest = assistant_messages[-1]
                return {
                    "status": "ok",
                    "runId": run_id,
                    "reply": self._message_content(latest),
                    "message": latest,
                    "messages": messages,
                }

        final_history = self.get_session_history(session_key, limit=100)
        return {
            "status": "timeout",
            "runId": run_id,
            "error": f"Agent did not respond within {timeout} seconds",
            "messages": self._extract_messages(final_history),
        }

    # ==================== PRIVATE HELPERS ====================

    def _post_json(
        self,
        path: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        timeout: int,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            return {
                "status": "error",
                "ok": False,
                "error": str(exc),
                "url": url,
            }

        try:
            data = response.json()
        except ValueError:
            return {
                "status": "error",
                "ok": False,
                "error": "Non-JSON response",
                "status_code": response.status_code,
                "text": response.text,
                "url": url,
            }

        if isinstance(data, dict):
            data.setdefault("ok", response.ok)
            data.setdefault("status_code", response.status_code)
        return data

    def _extract_messages(self, history_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = history_result.get("result", {}) if isinstance(history_result, dict) else {}
        messages = result.get("messages", [])
        return messages if isinstance(messages, list) else []

    def _collect_message_ids(self, messages: List[Dict[str, Any]]) -> set:
        ids = set()
        for msg in messages:
            for key in ("id", "messageId", "uuid"):
                value = msg.get(key)
                if value:
                    ids.add(str(value))
        return ids

    def _filter_new_messages(
        self,
        messages: List[Dict[str, Any]],
        baseline_ids: set,
        baseline_len: int,
    ) -> List[Dict[str, Any]]:
        new_messages: List[Dict[str, Any]] = []
        for idx, msg in enumerate(messages):
            msg_id = None
            for key in ("id", "messageId", "uuid"):
                value = msg.get(key)
                if value:
                    msg_id = str(value)
                    break

            if msg_id:
                if msg_id not in baseline_ids:
                    new_messages.append(msg)
            elif idx >= baseline_len:
                new_messages.append(msg)

        return new_messages

    def _message_role(self, message: Dict[str, Any]) -> str:
        return str(message.get("role") or message.get("type") or "").lower()

    def _message_content(self, message: Dict[str, Any]) -> str:
        content = message.get("content", "")
        if isinstance(content, list):
            return "\n".join(str(item) for item in content)
        return str(content or "")

    def _get_hooks_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.hooks_token}",
            "Content-Type": "application/json",
        }

    def _get_gateway_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.gateway_token}",
            "Content-Type": "application/json",
        }


def create_client(
    host: str,
    hooks_token: str,
    gateway_token: str,
    timeout: int = 30,
) -> OpenClawClient:
    """建立 OpenClaw Client"""
    config = OpenClawConfig(
        host=host,
        hooks_token=hooks_token,
        gateway_token=gateway_token,
        timeout=timeout,
    )
    return OpenClawClient(config)


if __name__ == "__main__":
    client = create_client(
        host="10.18.0.24:18789",
        hooks_token="shared-secret",
        gateway_token="your-gateway-token",
    )

    print(client.wake("System check"))
    print(client.call_agent(message="Hello, who are you?", agent_id="main", deliver=False))
    print(client.call_agent_sync(message="Summarize today's tasks", agent_id="main", session_key="hook:worker:test", timeout=120))
    print(client.list_sessions(limit=10))
    print(client.get_session_history("main", limit=10))
