import requests

BASE_URL = "http://127.0.0.1:8000"

print("Reset:", requests.get(f"{BASE_URL}/reset").json())
print("Step:", requests.post(f"{BASE_URL}/step", params={"action": "right"}).json())