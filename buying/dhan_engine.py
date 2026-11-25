# This file has been organized into the dedicated automation subfolder:
# Location: C:\Users\shakhan32\Desktop\trading\dhan_automation\dhan_engine.py

from dhan_automation.dhan_engine import *

if __name__ == "__main__":
    from dhan_automation.dhan_engine import test_connection, CLIENT_ID, ACCESS_TOKEN
    print("[*] Running Dhan Engine from dhan_automation/ ...")
    test_connection()
