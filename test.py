"""
Test script for OpenClaw Webhook Client

Usage:
    python test.py                               # Test sync call
    python test.py --async                       # Test async call
    python test.py --sessions                    # List sessions
    python test.py --history                     # Get session history
    python test.py --wake                        # Test wake endpoint
    python test.py --message "Hello"             # Override message
    python test.py --deliver                     # Deliver async reply to last channel
"""

import argparse
import json

import config
from openclaw_client import OpenClawClient, create_client


def get_client() -> OpenClawClient:
    """Create OpenClaw client from config"""
    return create_client(
        host=config.OPENCLAW_HOST,
        hooks_token=config.OPENCLAW_HOOKS_TOKEN,
        gateway_token=config.OPENCLAW_TOKEN,
        timeout=30,
    )


def print_result(title: str, result):
    print("=" * 50)
    print(title)
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def test_sync_call(client: OpenClawClient, args):
    """Test synchronous agent call"""
    result = client.call_agent_sync(
        message=args.message,
        name=args.name,
        agent_id=args.agent,
        session_key=args.session_key,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
        deliver=args.deliver,
        channel=args.channel,
        to=args.to,
        model=args.model,
        thinking=args.thinking,
        wake_mode=args.wake_mode,
    )
    print_result("Testing SYNC call_agent_sync()", result)
    return result


def test_async_call(client: OpenClawClient, args):
    """Test asynchronous agent call"""
    result = client.call_agent(
        message=args.message,
        name=args.name,
        agent_id=args.agent,
        session_key=args.session_key,
        deliver=args.deliver,
        channel=args.channel,
        to=args.to,
        model=args.model,
        thinking=args.thinking,
        wake_mode=args.wake_mode,
        timeout_seconds=args.timeout,
        request_timeout=args.request_timeout,
    )
    print_result("Testing ASYNC call_agent()", result)
    return result


def test_wake(client: OpenClawClient, args):
    """Test wake endpoint"""
    result = client.wake(args.message, mode=args.wake_mode)
    print_result("Testing wake()", result)
    return result


def test_list_sessions(client: OpenClawClient, args):
    """Test list sessions"""
    result = client.list_sessions(
        kinds=args.kinds,
        limit=args.limit,
        active_minutes=args.active_minutes,
    )
    print_result("Testing list_sessions()", result)
    return result


def test_session_history(client: OpenClawClient, args, session_key: str):
    """Test get session history"""
    result = client.get_session_history(
        session_key=session_key,
        limit=args.limit,
        include_tools=args.include_tools,
    )
    print_result(f"Testing get_session_history({session_key})", result)
    return result


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Webhook Client Test")
    parser.add_argument("--async", dest="async_mode", action="store_true", help="Test async call")
    parser.add_argument("--sessions", action="store_true", help="List sessions")
    parser.add_argument("--history", nargs="?", default=None, help="Get session history (optional session key)")
    parser.add_argument("--wake", action="store_true", help="Test wake endpoint")

    parser.add_argument("--agent", default="kevin", help="Agent ID to use")
    parser.add_argument("--session-key", default="hook:kevin:test", help="Session key to use")
    parser.add_argument("--name", default=None, help="Optional hook name")
    parser.add_argument("--message", default="你好嗎?你係邊個?", help="Message text to send")
    parser.add_argument("--timeout", type=int, default=120, help="Run timeout in seconds")
    parser.add_argument("--request-timeout", type=int, default=30, help="HTTP request timeout in seconds")
    parser.add_argument("--poll-interval", type=int, default=2, help="Polling interval for sync call")
    parser.add_argument("--wake-mode", default="now", choices=["now", "next-heartbeat"], help="Wake mode")
    parser.add_argument("--deliver", action="store_true", help="Deliver reply to messaging channel")
    parser.add_argument("--channel", default=None, help="Delivery channel")
    parser.add_argument("--to", default=None, help="Delivery target")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--thinking", default=None, help="Thinking override")

    parser.add_argument("--limit", type=int, default=10, help="Limit for sessions/history")
    parser.add_argument("--active-minutes", type=int, default=None, help="Only list recently active sessions")
    parser.add_argument("--kinds", nargs="*", default=None, help="Session kinds filter")
    parser.add_argument("--include-tools", action="store_true", help="Include tool messages in history")

    args = parser.parse_args()
    client = get_client()

    if args.wake:
        test_wake(client, args)
    elif args.sessions:
        test_list_sessions(client, args)
    elif args.history is not None:
        session_key = args.history or args.session_key
        test_session_history(client, args, session_key)
    elif args.async_mode:
        test_async_call(client, args)
    else:
        test_sync_call(client, args)


if __name__ == "__main__":
    main()
