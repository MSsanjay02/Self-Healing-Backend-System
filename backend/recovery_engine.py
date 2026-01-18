import subprocess
import os
from datetime import datetime

DEMO_APP_PATH = os.path.join("demo_app", "demo_service.py")

# ✅ This flag ensures CMD opens only once
CMD_OPENED_ONCE = False


def start_demo_service_once():
    """
    Opens demo CMD ONLY ONCE.
    After first time, it will NOT open new CMD windows again.
    """
    global CMD_OPENED_ONCE

    if CMD_OPENED_ONCE:
        return False, "Demo CMD already opened once (skipping)"

    # Kill old demo process if exists
    subprocess.run(
        'wmic process where "CommandLine like \'%demo_service.py%\'" call terminate',
        shell=True,
        capture_output=True
    )

    # Start new CMD window
    subprocess.Popen(
        ["python", DEMO_APP_PATH],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    CMD_OPENED_ONCE = True
    return True, f"Demo service CMD opened at {datetime.now()}"
