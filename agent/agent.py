import time
import psutil
from datetime import datetime


def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    return cpu_usage, memory_usage


def main():
    print("Starting System Monitoring Agent...\n")

    while True:
        cpu, memory = get_system_metrics()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"{timestamp} | CPU Usage: {cpu}% | Memory Usage: {memory}%")

        time.sleep(0.1)


if __name__ == "__main__":
    main()
