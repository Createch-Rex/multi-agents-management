import requests
import config
import json


data = {
  "tool": "sessions_send",
  "args": {
    "message": "Who are you?",
    "sessionKey": "agent:main:mam-test",
    "timeoutSeconds": 120,
    "mode": "run",
    "streamTo": "parent"
  },
}

header = {
    "Authorization": f"Bearer {config.OPENCLAW_TOKEN}"
}
web = requests.post(f'http://{config.OPENCLAW_HOST}/tools/invoke', json=data, headers=header)
response = json.dumps(web.json(), ensure_ascii=False, indent=2)
print(response)
