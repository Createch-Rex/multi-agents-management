import sys
import os


if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.getcwd()

STATIC_DIR = os.path.join(ROOT_DIR, 'static')
WEB_DIR = os.path.join(STATIC_DIR, 'web')
MEDIA_DIR = os.path.join(STATIC_DIR, 'media')

# Runtime credentials and deployment-specific hosts must be supplied through
# the environment. Keep secrets out of the repository and use a local .env
# file or the hosting platform's secret store during development/deployment.
SYSTEM_KEY = os.getenv("SYSTEM_KEY", "")

DATABASE_NAME = os.getenv("DATABASE_NAME", "multi_agent_management")
DATABASE_HOST = os.getenv("DATABASE_HOST", "")
DATABASE_USER = os.getenv("DATABASE_USER", "")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "3306"))

OPENCLAW_HOST = os.getenv("OPENCLAW_HOST", "")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")

# Webhook config (for /hooks/agent endpoint). This is separate from the
# gateway auth token.
OPENCLAW_HOOKS_TOKEN = os.getenv("OPENCLAW_HOOKS_TOKEN", "")
OPENCLAW_HOOKS_PATH = os.getenv("OPENCLAW_HOOKS_PATH", "/hooks/agent")

# Sessions API (for polling agent response)
OPENCLAW_SESSIONS_PATH = os.getenv("OPENCLAW_SESSIONS_PATH", "/tools/invoke")
