import ast
import re
from colorama import Fore, Style

def colored_print(text, color=Fore.WHITE, end='\n'):
    print(f"{color}{text}{Style.RESET_ALL}", end=end)

def validate_code(code):
    try:
        ast.parse(code)
        colored_print("Code validation passed.", Fore.GREEN)
        return True
    except SyntaxError as e:
        colored_print(f"Syntax error in generated code: {e}", Fore.RED)
        return False

def review_code_safety(code):
    # Remove comments from the code
    code_without_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    
    unsafe_patterns = [
        r'\bos\.remove\b',
        r'\bos\.unlink\b',
        r'\bos\.rmdir\b',
        r'\bshutil\.rmtree\b',
        r'\bsubprocess\b',
        r'\beval\b',
        r'\bexec\b',
        r'\b__import__\b',
        r'\bopen\([^,]+,\s*[\'"]w[\'"]\)',  # Be cautious with write mode
    ]
    for pattern in unsafe_patterns:
        if re.search(pattern, code_without_comments):
            colored_print(f"Warning: Potentially unsafe operation detected: {pattern}", Fore.RED)
            return False
    
    # Check for safe use of zipfile
    if 'zipfile.ZipFile' in code_without_comments:
        if not re.search(r'zipfile\.ZipFile\([^,]+,\s*[\'"]r[\'"]\)', code_without_comments) and \
           not re.search(r'zipfile\.ZipFile\([^,]+,\s*[\'"]w[\'"]\)', code_without_comments):
            colored_print("Warning: Potentially unsafe use of zipfile.ZipFile detected", Fore.RED)
            return False
    
    colored_print("Code safety review passed.", Fore.GREEN)
    return True