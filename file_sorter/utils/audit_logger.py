from datetime import datetime
import os

LOG_FILE = "audit_trail.log"

def log_action(action, filename="", details=""):
    """Write actions to audit log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"{timestamp} | {action} | {filename} | {details}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass
