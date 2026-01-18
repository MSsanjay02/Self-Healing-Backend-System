import time
import psutil
import requests
from datetime import datetime

BACKEND_URL = "http://localhost:8000/metrics"


def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    return cpu_usage, memory_usage


def create_payload(cpu, memory):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage": cpu,
        "memory_usage": memory
    }


def send_metrics(payload):
    try:
        response = requests.post(BACKEND_URL, json=payload)
        print(f"Sent data | Status Code: {response.status_code}")

        if response.headers.get("content-type", "").startswith("application/json"):
            print("Backend response:", response.json())
        else:
            print("Backend response (non-JSON):", response.text[:200])

    except Exception as e:
        print(f"Error sending data: {e}")


def main():
    print("System Monitoring Agent started...\n")

    while True:
        cpu, memory = get_system_metrics()
        payload = create_payload(cpu, memory)
        payload["memory_usage"] = 5.0 


        print(payload)
        send_metrics(payload)

        time.sleep(1)


if __name__ == "__main__":
    main()
