from concurrent.futures import ThreadPoolExecutor
from requests import get
from requests.auth import HTTPBasicAuth


BASE_URL = "http://127.0.0.1:5000/rest"
auth = HTTPBasicAuth("admin", "admin")

def send_is_alive_request():
    if get(f"{BASE_URL}/is_alive").status_code != 200:
        print("error")

def send_get_instance_request():
    request = get(f"{BASE_URL}/instance/device/Washington", auth=auth)
    if request.status_code != 200:
        print(request)

with ThreadPoolExecutor(max_workers=10) as pool:
    for _ in range(100):
        pool.submit(send_get_instance_request)
