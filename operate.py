import io
import sys
import os
import re
import importlib
import shutil
import zipfile
from send2trash import send2trash
from core.api_engine import APIEngine
from core.safety_checker import validate_code, review_code_safety
from core.conflict_resolver import resolve_conflicts
from core.logger import log_successful_execution
from core.utils import load_sample_code, detect_imports, ask_permission
from core.zip_operations import preview_zip_changes, preview_unzip_changes, execute_zip_changes, execute_unzip_changes
from core.code_generator import generate_code, extract_python_code, clean_generated_code
from core.code_modifier import replace_delete_with_trash, add_print_statements
from core.file_operations import preview_changes, execute_changes

ROOT_PATH = r"D:\AI\Projects\Code\FileBotler\test"
DEFAULT_INSTRUCTION = ""
JSON_LOG_PATH = "successful_executions.json"
MAX_RETRIES = 5

def generate_and_validate_code(user_input, sample_code):
    context = ""
    for attempt in range(MAX_RETRIES):
        generated_code = generate_code(user_input, sample_code, context)
        print(f"\nAttempt {attempt + 1} - Generated Code:")
        print(generated_code)

        extracted_code = extract_python_code(generated_code)
        if not extracted_code:
            context += "\nFailed to extract valid Python code. Please generate only the required functions without any explanations or comments."
            continue

        if not validate_code(extracted_code):
            context += "\nPrevious attempt failed code validation. Ensure the code is syntactically correct."
            continue

        if not review_code_safety(extracted_code):
            context += "\nPrevious attempt failed safety review. Use send2trash for file/folder removal operations."
            continue

        extracted_code = replace_delete_with_trash(extracted_code)

        if 'print' not in extracted_code:
            extracted_code = add_print_statements(extracted_code)
            print("Added print statements to the generated code:")
            print(extracted_code)

        namespace = create_execution_namespace()
        
        try:
            exec(extracted_code, namespace)
        except Exception as e:
            context += f"\nError executing generated code: {str(e)}"
            continue
        
        if 'preview_changes' not in namespace or 'execute_changes' not in namespace:
            context += "\nPrevious attempt did not include both preview_changes and execute_changes functions."
            continue

        preview_output = capture_preview_output(namespace['preview_changes'], ROOT_PATH)

        if not preview_output.strip():
            context += "\nPrevious attempt didn't produce any output in preview_changes. Ensure to print each proposed change."
            continue

        changes = namespace['preview_changes'](ROOT_PATH)

        if not changes:
            context += "\nPrevious attempt didn't propose any changes. Ensure the code correctly identifies files or folders to be modified."
            continue

        print("Preview output:")
        print(preview_output)

        return extracted_code, changes, preview_output

    print(f"Code generation failed after {MAX_RETRIES} attempts. Please try a different request.")
    return None, None, None

def capture_preview_output(preview_func, root_path):
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    preview_func(root_path)
    preview_output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return preview_output

def create_execution_namespace():
    return {
        'ROOT_PATH': ROOT_PATH, 
        'os': os, 
        're': re, 
        'shutil': shutil, 
        'zipfile': zipfile,
        'send2trash': send2trash,
    }

def main():
    sample_code = load_sample_code()
    
    if DEFAULT_INSTRUCTION:
        user_input = DEFAULT_INSTRUCTION
    else:
        user_input = input("Enter your file operation request: ")
    
    print(f"\nInstruction: {user_input}")

    generated_code, changes, preview_output = generate_and_validate_code(user_input, sample_code)
    if generated_code is None:
        return

    print("\nPreviewing changes:")
    preview_changes(changes)

    resolved_changes = resolve_conflicts(changes)
    if resolved_changes is None:
        print("Operation cancelled due to conflicts.")
        return

    if resolved_changes != changes:
        print("\nConflicts resolved. Updated preview:")
        preview_changes(resolved_changes)

    if any(change[0] in ["delete"] for change in resolved_changes):
        print("\nWARNING: This operation will move files or folders to the trash.")
        user_confirm = input("Are you sure you want to proceed? (Y/N): ")
        if user_confirm.lower() != 'y':
            print("Operation cancelled.")
            return

    user_confirm = input("\nDo you want to execute these changes? (Y/N): ")
    if user_confirm.lower() == 'y':
        try:
            execute_changes(resolved_changes)
            log_successful_execution(user_input, generated_code)
        except Exception as e:
            print(f"Error during execution: {e}")
            print("Generated code:")
            print(generated_code)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()