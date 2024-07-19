import io
import sys
import os
import re
import importlib
import shutil
import zipfile
import random
import math
import datetime
import json
import csv
from send2trash import send2trash
from PIL import Image
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Try to import Wand, but don't fail if it's not available
try:
    from wand.image import Image as WandImage
    WAND_AVAILABLE = True
except ImportError:
    WAND_AVAILABLE = False
    print(Fore.RED + "WARNING: ImageMagick (Wand) is not available. Some image operations may be limited.")

from core.api_engine import APIEngine
from core.safety_checker import validate_code, review_code_safety
from core.conflict_resolver import resolve_conflicts
from core.logger import log_successful_execution
from core.utils import load_sample_code, detect_imports, ask_permission
from core.zip_operations import preview_zip_changes, preview_unzip_changes, execute_zip_changes, execute_unzip_changes
from core.code_generator import generate_code, extract_python_code, clean_generated_code, fix_send2trash_usage
from core.code_modifier import replace_delete_with_trash, add_print_statements
from core.file_operations import preview_changes as core_preview_changes, execute_changes as core_execute_changes
from core.file_creation import create_file, colored_print as file_creation_colored_print

ROOT_PATH = r"D:\AI\Projects\Code\FileBotler\test"
DEFAULT_INSTRUCTION = ""
JSON_LOG_PATH = "successful_executions.json"
MAX_RETRIES = 5

def colored_print(text, color=Fore.WHITE, end='\n'):
    print(f"{color}{text}{Style.RESET_ALL}", end=end)

def capture_preview_output(preview_func, root_path):
    old_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        changes = preview_func(root_path)
        preview_output = captured_output.getvalue().strip()
    except Exception as e:
        preview_output = f"Error during preview_changes: {str(e)}"
        changes = []
    finally:
        sys.stdout = old_stdout
    return changes, preview_output

def generate_and_validate_code(user_input, sample_code):
    context = ""
    for attempt in range(MAX_RETRIES):
        attempt_color = Fore.YELLOW if attempt % 2 == 0 else Fore.LIGHTYELLOW_EX
        
        colored_print(f"\nAttempt {attempt + 1} - Generated Code:", attempt_color)
        generated_code = generate_code(user_input, sample_code)
        colored_print(generated_code, attempt_color)

        extracted_code = extract_python_code(generated_code)
        if not extracted_code:
            colored_print("Failed to extract valid Python code. Please generate only the required functions without any explanations or comments.", Fore.RED)
            context += "\nFailed to extract valid Python code. Please generate only the required functions without any explanations or comments."
            continue

        if not validate_code(extracted_code):
            colored_print("Code validation failed. Ensure the code is syntactically correct.", Fore.RED)
            context += "\nPrevious attempt failed code validation. Ensure the code is syntactically correct."
            continue

        if not review_code_safety(extracted_code):
            colored_print("Safety review failed. Use send2trash for file and folder removal operations.", Fore.RED)
            context += "\nPrevious attempt failed safety review. Use send2trash for file and folder removal operations."
            continue

        extracted_code = replace_delete_with_trash(extracted_code)
        extracted_code = fix_send2trash_usage(extracted_code)

        namespace = create_execution_namespace()
        
        try:
            exec(extracted_code, namespace)
        except Exception as e:
            colored_print(f"Error executing generated code: {str(e)}", Fore.RED)
            context += f"\nError executing generated code: {str(e)}"
            continue
        
        if 'preview_changes' not in namespace or 'execute_changes' not in namespace:
            colored_print("Generated code is missing preview_changes or execute_changes functions.", Fore.RED)
            context += "\nPrevious attempt did not include both preview_changes and execute_changes functions."
            continue

        changes, preview_output = capture_preview_output(namespace['preview_changes'], ROOT_PATH)

        if not preview_output.strip():
            colored_print("No preview output generated. Ensure the preview_changes function prints each proposed change.", Fore.RED)
            context += "\nPrevious attempt didn't produce any output in preview_changes. Ensure to print each proposed change."
            continue

        if not changes:
            colored_print("No changes proposed. Ensure the code correctly identifies files or folders to be modified.", Fore.RED)
            context += "\nPrevious attempt didn't propose any changes. Ensure the code correctly identifies files or folders to be modified."
            continue

        colored_print("\nPreviewing changes:", Fore.CYAN)
        colored_print(preview_output.strip(), Fore.LIGHTYELLOW_EX)

        return extracted_code, changes, preview_output, namespace['execute_changes']

    colored_print(f"Code generation failed after {MAX_RETRIES} attempts. Please try a different request.", Fore.RED)
    return None, None, None, None

def create_execution_namespace():
    namespace = {
        'ROOT_PATH': ROOT_PATH, 
        'os': os, 
        're': re, 
        'shutil': shutil, 
        'zipfile': zipfile,
        'send2trash': send2trash,
        'create_file': create_file,
        'file_creation': sys.modules[create_file.__module__],
        'random': random,
        'math': math,
        'datetime': datetime,
        'json': json,
        'csv': csv,
        'Image': Image,
        'WAND_AVAILABLE': WAND_AVAILABLE,
        'colored_print': file_creation_colored_print,
    }
    if WAND_AVAILABLE:
        namespace['WandImage'] = WandImage
    return namespace

def main():
    sample_code = load_sample_code()
    
    colored_print("Welcome to FileBotler!", Fore.CYAN)
    
    user_input = input("Enter your file operation request: ")
    
    colored_print(f"\nInstruction: {user_input}", Fore.CYAN)

    generated_code, changes, preview_output, execute_changes_func = generate_and_validate_code(user_input, sample_code)
    if generated_code is None:
        return

    colored_print("\nPreviewing changes:", Fore.CYAN)
    colored_print(preview_output.strip(), Fore.LIGHTYELLOW_EX)

    user_confirm = input("Do you want to execute these changes? (Y/N): ").strip().lower()
    if user_confirm != 'y':
        colored_print("Operation cancelled.", Fore.RED)
        return

    resolved_changes = resolve_conflicts(changes)
    if resolved_changes is None:
        colored_print("Operation cancelled due to conflicts.", Fore.RED)
        return

    if resolved_changes != changes:
        colored_print("\nConflicts resolved. Updated preview:", Fore.CYAN)
        core_preview_changes(resolved_changes)

    if any(change[0] in ["delete"] for change in resolved_changes):
        colored_print("\nWARNING: This operation will move files or folders to the trash.", Fore.RED)
        user_confirm = input("Are you sure you want to proceed? (Y/N): ")
        if user_confirm.lower() != 'y':
            colored_print("Operation cancelled.", Fore.RED)
            return

    try:
        namespace = create_execution_namespace()
        namespace['execute_changes'] = execute_changes_func
        exec(generated_code, namespace)
        namespace['execute_changes'](resolved_changes)
        colored_print("Changes executed successfully.", Fore.CYAN)
        
        save_log = input("Do you want to save this execution to the log? (Y/N): ")
        if save_log.lower() == 'y':
            log_successful_execution(user_input, generated_code)
            colored_print(f"Execution logged successfully in {JSON_LOG_PATH}", Fore.CYAN)
        else:
            colored_print("Execution not logged.", Fore.CYAN)
    except Exception as e:
        colored_print(f"Error during execution: {str(e)}", Fore.RED)
        colored_print("Generated code:", Fore.RED)
        colored_print(generated_code, Fore.RED)
        colored_print("\nPlease review the generated code and try again.", Fore.RED)

if __name__ == "__main__":
    main()
