"""
OpenClaw Webhook Client

提供 OpenClaw Webhook API 同 tools invoke 嘅 Python 封裝。

Endpoints:
- POST /hooks/wake      - 觸發 main session heartbeat
- POST /hooks/agent     - 觸發 isolated agent run
- POST /hooks/<name>    - 調用自定義 mapped hook
- POST /tools/invoke    - 調用 tool (sessions_list / sessions_history 等)
"""

import json
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

    def wake(self, text: str, mode: str = "now") -> Dict[str, Any]:
        """POST /hooks/wake - 觸發 main session heartbeat"""
        return self._post_json(
            path=f"{self.config.hooks_path}/wake",
            payload={"text": text, "mode": mode},
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
        """POST /hooks/agent - 觸發 isolated agent run"""
        data: Dict[str, Any] = {
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

    def call_mapped_hook(self, hook_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /hooks/<name> - 調用自定義 mapping hook"""
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
        """POST /tools/invoke - 調用 OpenClaw tool"""
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

    def get_session_history(self, session_key: str, limit: int = 20, include_tools: bool = False) -> Dict[str, Any]:
        return self.invoke_tool("sessions_history", {
            "sessionKey": session_key,
            "limit": limit,
            "includeTools": include_tools,
        })

    def get_session_history_details(self, session_key: str, limit: int = 20, include_tools: bool = False) -> Dict[str, Any]:
        result = self.get_session_history(session_key, limit=limit, include_tools=include_tools)
        return self._extract_result_details(result)

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

    def list_sessions_details(
        self,
        kinds: Optional[List[str]] = None,
        limit: int = 50,
        active_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        result = self.list_sessions(kinds=kinds, limit=limit, active_minutes=active_minutes)
        return self._extract_result_details(result)

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
        """同步呼叫 Agent (先 webhook，再 poll sessions_history 等回覆)"""
        baseline_result = self.get_session_history_details(session_key, limit=100, include_tools=True)
        baseline_messages = self._extract_messages_from_details(baseline_result)
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
            history_result = self.get_session_history_details(session_key, limit=100, include_tools=True)
            messages = self._extract_messages_from_details(history_result)
            new_messages = self._filter_new_messages(messages, baseline_ids, baseline_len)

            candidate_messages = []
            for msg in new_messages:
                if self._message_role(msg) != "assistant":
                    continue
                normalized = self._message_text(msg)
                if normalized.strip():
                    candidate_messages.append({
                        "raw": msg,
                        "text": normalized,
                    })

            if candidate_messages:
                latest = candidate_messages[-1]
                return {
                    "status": "ok",
                    "runId": run_id,
                    "reply": latest["text"],
                    "message": latest["raw"],
                    "messages": messages,
                    "details": history_result,
                }

        final_history = self.get_session_history_details(session_key, limit=100, include_tools=True)
        return {
            "status": "timeout",
            "runId": run_id,
            "error": f"Agent did not respond within {timeout} seconds",
            "messages": self._extract_messages_from_details(final_history),
            "details": final_history,
        }

    # ==================== PRIVATE HELPERS ====================

    def _post_json(self, path: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int) -> Dict[str, Any]:
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

    def _extract_result_details(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        result = tool_result.get("result", {}) if isinstance(tool_result, dict) else {}
        if isinstance(result, dict):
            details = result.get("details")
            if isinstance(details, dict):
                return details

            content = result.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text")
                        if isinstance(text, str):
                            try:
                                parsed = json.loads(text)
                                if isinstance(parsed, dict):
                                    return parsed
                            except json.JSONDecodeError:
                                pass
        return {}

    def _extract_messages_from_details(self, details: Dict[str, Any]) -> List[Dict[str, Any]]:
        messages = details.get("messages", []) if isinstance(details, dict) else []
        return messages if isinstance(messages, list) else []

    def _collect_message_ids(self, messages: List[Dict[str, Any]]) -> set:
        ids = set()
        for msg in messages:
            for key in ("id", "messageId", "uuid", "timestamp"):
                value = msg.get(key)
                if value is not None:
                    ids.add(str(value))
                    break
        return ids

    def _filter_new_messages(self, messages: List[Dict[str, Any]], baseline_ids: set, baseline_len: int) -> List[Dict[str, Any]]:
        new_messages: List[Dict[str, Any]] = []
        for idx, msg in enumerate(messages):
            identity = None
            for key in ("id", "messageId", "uuid", "timestamp"):
                value = msg.get(key)
                if value is not None:
                    identity = str(value)
                    break

            if identity is not None:
                if identity not in baseline_ids:
                    new_messages.append(msg)
            elif idx >= baseline_len:
                new_messages.append(msg)
        return new_messages

    def _message_role(self, message: Dict[str, Any]) -> str:
        return str(message.get("role") or message.get("type") or "").lower()

    def _message_text(self, message: Dict[str, Any]) -> str:
        content = message.get("content", "")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                    continue
                if not isinstance(item, dict):
                    continue

                item_type = item.get("type")
                if item_type in ("text", "output_text"):
                    text = item.get("text")
                    if text:
                        parts.append(str(text))
                elif item_type == "input_text":
                    text = item.get("text")
                    if text:
                        parts.append(str(text))
            return "\n".join(part for part in parts if part).strip()

        if isinstance(content, dict):
            if isinstance(content.get("text"), str):
                return content["text"]

        return ""

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


def create_client(host: str, hooks_token: str, gateway_token: str, timeout: int = 30) -> OpenClawClient:
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
