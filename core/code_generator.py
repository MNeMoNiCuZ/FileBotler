import re
import os
from core.api_engine import APIEngine

def load_code_generation_prompt():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(script_dir, 'prompts', 'code_generation_prompt.txt')
    try:
        with open(prompt_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Code generation prompt file not found at {prompt_path}")
        print("Please ensure the file exists and try again.")
        exit(1)

def generate_code(user_input, sample_code, context=""):
    api_engine = APIEngine(engine='openai')  # Adjust the engine as needed
    code_generation_prompt = load_code_generation_prompt()
    
    prompt = {
        "messages": [
            {"role": "system", "content": f"{code_generation_prompt}\n\nUse the following sample code structure as a guide:\n\n{sample_code}"},
            {"role": "user", "content": f"Generate Python code to: {user_input}\n\nAdditional context: {context}\n\nIMPORTANT: Use send2trash instead of os.remove or os.rmdir for file and folder removal operations."}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    response = api_engine.call_api(prompt)
    return clean_generated_code(response)

def clean_generated_code(code):
    code = re.sub(r'```python|```', '', code)
    return code.strip()

def extract_python_code(text):
    code_blocks = re.findall(r'```python(.*?)```', text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    functions = re.findall(r'def\s+\w+\s*\(.*?\):.*?(?=\n\n|\Z)', text, re.DOTALL)
    if len(functions) >= 2:
        return '\n\n'.join(functions)
    
    return None