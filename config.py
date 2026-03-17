import sys
import os


if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.getcwd()

STATIC_DIR = os.path.join(ROOT_DIR, 'static')
WEB_DIR = os.path.join(STATIC_DIR, 'web')
MEDIA_DIR = os.path.join(STATIC_DIR, 'media')

SYSTEM_KEY = "61p7i5b69sIDwk94LfF5EafmVDv4KzGO"

DATABASE_NAME = "multi_agent_management"
DATABASE_HOST = "10.18.0.30"
DATABASE_USER = "root"
DATABASE_PASSWORD = "QazWsxEdc$@3649"
DATABASE_PORT = 3306

OPENCLAW_HOST = "10.18.0.24:18789"
OPENCLAW_TOKEN = "e21f26600d41d7979aa7e78529d250732557caed5add5e56"

# Webhook config (for /hooks/agent endpoint)
# This is separate from gateway auth token
OPENCLAW_HOOKS_TOKEN = "shared-secret"
OPENCLAW_HOOKS_PATH = "/hooks/agent"
