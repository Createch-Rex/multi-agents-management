"""
Test script for OpenClaw Webhook Client

Usage:
    python test.py              # Test sync call
    python test.py --async      # Test async call
    python test.py --sessions   # List sessions
    python test.py --history    # Get session history
"""

import argparse
import json
from openclaw_client import create_client, OpenClawClient
import config


def get_client() -> OpenClawClient:
    """Create OpenClaw client from config"""
    return create_client(
        host=config.OPENCLAW_HOST,
        hooks_token=config.OPENCLAW_HOOKS_TOKEN,
        gateway_token=config.OPENCLAW_TOKEN,
        timeout=120
    )


def test_sync_call(client: OpenClawClient):
    """Test synchronous agent call"""
    print("=" * 50)
    print("Testing SYNC call_agent_sync()")
    print("=" * 50)
    
    result = client.call_agent_sync(
        message="你好嗎?你係邊個?",
        agent_id="kevin",
        session_key="hook:kevin:test",
        timeout=120
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def test_async_call(client: OpenClawClient):
    """Test asynchronous agent call"""
    print("=" * 50)
    print("Testing ASYNC call_agent()")
    print("=" * 50)
    
    result = client.call_agent(
        message="Hello, who are you?",
        agent_id="kevin",
        session_key="hook:kevin:test",
        deliver=False,
        timeout_seconds=120
    )
    
    print(f"Webhook triggered: {result}")
    
    if result.get("status") == "accepted":
        run_id = result.get("runId")
        print(f"RunId: {run_id}")
        print("Agent is running... Poll session history for response.")
    
    return result


def test_wake(client: OpenClawClient):
    """Test wake endpoint"""
    print("=" * 50)
    print("Testing wake()")
    print("=" * 50)
    
    result = client.wake("Test wake from Python client")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def test_list_sessions(client: OpenClawClient):
    """Test list sessions"""
    print("=" * 50)
    print("Testing list_sessions()")
    print("=" * 50)
    
    result = client.list_sessions(limit=10)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def test_session_history(client: OpenClawClient, session_key: str):
    """Test get session history"""
    print("=" * 50)
    print(f"Testing get_session_history({session_key})")
    print("=" * 50)
    
    result = client.get_session_history(session_key, limit=10)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Webhook Client Test")
    parser.add_argument("--async", dest="async_mode", action="store_true", help="Test async call")
    parser.add_argument("--sessions", action="store_true", help="List sessions")
    parser.add_argument("--history", nargs="?", default=None, help="Get session history (optional session key)")
    parser.add_argument("--wake", action="store_true", help="Test wake endpoint")
    parser.add_argument("--agent", default="kevin", help="Agent ID to use")
    parser.add_argument("--session-key", default="hook:kevin:test", help="Session key to use")
    
    args = parser.parse_args()
    
    client = get_client()
    
    if args.wake:
        test_wake(client)
    elif args.sessions:
        test_list_sessions(client)
    elif args.history is not None:
        session_key = args.history or args.session_key
        test_session_history(client, session_key)
    elif args.async_mode:
        test_async_call(client)
    else:
        test_sync_call(client)


if __name__ == "__main__":
    main()