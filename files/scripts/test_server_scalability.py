from requests import get
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:5000/rest"

def send_is_alive_request():
    if get(f"{BASE_URL}/is_alive").status_code != 200:
        print("error")

def send_get_instance_request():
    if get(f"{BASE_URL}/get_instance/device/Washington").status_code != 200:
        print("error")

with ThreadPoolExecutor(max_workers=10) as pool:
    for _ in range(10_000):
        pool.submit(send_get_instance_request)
