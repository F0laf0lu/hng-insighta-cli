import base64
import hashlib
import http
import json
import random
import secrets
import socket
import string
from http.server import HTTPServer
import threading
from urllib.parse import parse_qs, urlparse
import webbrowser
import requests
from pathlib import Path

import click

"""
CLI generates state, code_verifier, code_challenge
CLI starts a temporary local server on something like http://localhost:8765/callback
CLI opens the GitHub OAuth URL in the browser using Python's webbrowser module
User authenticates in browser
GitHub redirects to http://localhost:8765/callback?code=xxx&state=xxx
Your temporary local server captures the code and state
CLI validates state, sends code + code_verifier to your backend
Backend exchanges with GitHub, creates user, returns your tokens
CLI stores tokens in ~/.insighta/credentials.json
Local server shuts down
"""
GITHUB_CLIENT_ID = "Ov23liAotIwnyJleTrA7"
GITHUB_CLIENT_SECRET = "e79012b96b97874887127bcdaef9b56ff2a35564"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def generate_secure_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


PORT = get_free_port()


class GITHubCallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        print(query_params)
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{'status':'success'}")


@click.command()
def login():

    STATE = generate_random_string(16)
    CODE_VERIFIER = generate_secure_string(43)
    sha256_hash = hashlib.sha256(CODE_VERIFIER.encode("utf-8")).digest()
    CODE_CHALLENGE = (
        base64.urlsafe_b64encode(sha256_hash).decode("utf-8").replace("=", "")
    )
    redirect_uri = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&code_challenge_method=S256&code_challenge={CODE_CHALLENGE}&scope=user&state={STATE}&redirect_uri=http://127.0.0.1:8765/callback"

    # THreading Event
    callback_received = threading.Event()
    callback_data = {}

    class GITHubCallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            callback_data.update(query_params)
            self.send_response(200, "OK")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{'status':'success'}")
            callback_received.set()

    server = HTTPServer(("", 8765), GITHubCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    webbrowser.open(redirect_uri)
    click.echo("Waiting for GitHub callback...")
    callback_received.wait()
    server.shutdown()

    code = callback_data.get("code", None)
    state = callback_data.get("state", None)

    if not code or not state:
        click.echo("Missing code and invalid code in callback. Run login command again")
        return

    if not code[0] or state[0] != STATE:
        click.echo("Missing code and invalid code in callback. Run login command again")
        return

    backend_url = "http://127.0.0.1:8000/auth/github/cli_callback"
    payload = {"code": code[0], "code_verifier": CODE_VERIFIER}
    headers = {"Accept": "application/json"}
    response = requests.post(url=backend_url, data=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        file.write(json.dumps(data))
    username = response.json()["user"]["username"]
    click.echo(f"Logged in. @{username}")


@click.command()
def logout():
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        access_token = content["tokens"]["access_token"]
        refresh_token = content["tokens"]["refresh_token"]
        backend_url = "http://127.0.0.1:8000/auth/logout"
        payload = {"refresh_token": refresh_token}
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(url=backend_url, data=payload, headers=headers)
        response.raise_for_status()
        click.echo(f"{response.json()['message']}")
        path.unlink(missing_ok=True)


@click.command()
def whoami():
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        username = content["user"]["username"]
        click.echo(f"@{username}")
