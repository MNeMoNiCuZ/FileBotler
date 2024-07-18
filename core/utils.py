import os
import ast

ALLOWED_MODULES = {'os', 're', 'shutil', 'zipfile'}

def load_sample_code():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_code_path = os.path.join(script_dir, 'prompts', 'sampleCode.txt')
    try:
        with open(sample_code_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Sample code file not found at {sample_code_path}")
        print("Please ensure the file exists and try again.")
        exit(1)

def detect_imports(code):
    tree = ast.parse(code)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
    return imports - ALLOWED_MODULES

def ask_permission(imports):
    if not imports:
        return {}
    
    print("\nThe generated code requires the following additional libraries:")
    for imp in imports:
        print(f"- {imp}")
    
    allowed_imports = {}
    for imp in imports:
        while True:
            response = input(f"Do you want to allow the use of '{imp}'? (Y/N): ").lower()
            if response in ['y', 'n']:
                allowed_imports[imp] = (response == 'y')
                break
            else:
                print("Invalid input. Please enter 'Y' or 'N'.")
    
    return allowed_imports