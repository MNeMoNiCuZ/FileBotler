import json
from datetime import datetime
import os

JSON_LOG_PATH = "successful_executions.json"

def log_successful_execution(instruction, code):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "instruction": instruction,
        "code": code
    }
    
    try:
        if os.path.exists(JSON_LOG_PATH):
            with open(JSON_LOG_PATH, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        data.append(log_entry)
        
        with open(JSON_LOG_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Execution logged successfully in {JSON_LOG_PATH}")
    except Exception as e:
        print(f"Error logging execution: {e}")