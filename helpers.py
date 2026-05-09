import json
from pathlib import Path
import time

import click
import jwt
import requests


def auto_refresh():
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return None
    with open(path, 'r') as file:
        content = json.loads(file.read())
        refresh_token = content['data']['refresh_token']
        access_token = content['data']['access_token']
        payload = jwt.decode(access_token, options={"verify_signature": False})
        expiry_time = payload["exp"]
        if time.time() > expiry_time:
            url = f"http://127.0.0.1:8000/auth/refresh"
            headers = {"Accept": "application/json", "Authorization":f"Bearer {access_token}", "X-API-Version":1}
            try:
                response = requests.post(url, json={'refresh_token':refresh_token}, headers=headers)
                response.raise_for_status()
            except Exception:
                click.echo("Token expired. Run login command again")
                return None
            data = response.json()
            new_access_token = data['tokens']['access_token']
            path = Path(Path.home(), ".insighta/credentials.json")
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as file:
                file.write(json.dumps(data))
            return new_access_token
    return access_token
