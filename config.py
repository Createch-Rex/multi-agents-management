import sys
import os


if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.getcwd()

STATIC_DIR = os.path.join(ROOT_DIR, 'static')

DATABASE_NAME = "multi_agent_management"
DATABASE_HOST = "10.18.0.30"
DATABASE_USER = "root"
DATABASE_PASSWORD = "QazWsxEdc$@3649"
DATABASE_PORT = 3306

OPENCLAW_URL = ""
OPENCLAW_TOKEN = ""
