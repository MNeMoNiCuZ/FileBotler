import ast
import re

def validate_code(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
        return False

def review_code_safety(code):
    unsafe_patterns = [
        r'os\.remove',
        r'os\.unlink',
        r'os\.rmdir',
        r'shutil\.rmtree',
        r'subprocess',
        r'eval',
        r'__import__',
        r'open\([^,]+,\s*[\'"]w[\'"]\)',  # Be cautious with write mode
    ]
    for pattern in unsafe_patterns:
        if re.search(pattern, code):
            print(f"Warning: Potentially unsafe operation detected: {pattern}")
            return False
    
    # Check for safe use of zipfile
    if 'zipfile.ZipFile' in code:
        if not re.search(r'zipfile\.ZipFile\([^,]+,\s*[\'"]r[\'"]\)', code) and \
           not re.search(r'zipfile\.ZipFile\([^,]+,\s*[\'"]w[\'"]\)', code):
            print("Warning: Potentially unsafe use of zipfile.ZipFile detected")
            return False
    
    return True
