# This file wraps the dedicated automation engine in dhan_automation/dhan_engine.py
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dhan_automation.dhan_engine import *  # noqa: F401, F403, E402

if __name__ == "__main__":
    from dhan_automation.dhan_engine import test_connection

    print("[*] Running Dhan Engine from dhan_automation/ ...")
    test_connection()
