import click
'''
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
'''

def login():
    pass