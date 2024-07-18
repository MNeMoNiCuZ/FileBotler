import os
import shutil
from send2trash import send2trash

def preview_changes(changes):
    for change in changes:
        op, params = change
        if op == "move":
            print(f"Would move: {params[0]} -> {params[1]}")
        elif op == "copy":
            print(f"Would copy: {params[0]} -> {params[1]}")
        elif op == "delete":
            print(f"Would delete: {params}")

def execute_changes(changes):
    for change in changes:
        op, params = change
        if op == "move":
            src, dst = params
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
        elif op == "copy":
            src, dst = params
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        elif op == "delete":
            send2trash(params)
    print("Changes executed successfully.")