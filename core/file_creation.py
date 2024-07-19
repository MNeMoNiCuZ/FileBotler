import os
import csv
import json
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

def colored_print(text, color=Fore.CYAN, end='\n'):
    print(f"{color}{text}{Style.RESET_ALL}", end=end)

def create_text_file(path, content=""):
    colored_print(f"Creating text file: {path}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    colored_print(f"Text file created successfully: {path}")
    return path

def create_csv_file(path, data, headers=None):
    colored_print(f"Creating CSV file: {path}")
    with open(path, 'w', newline='', encoding='utf-8') as f:
        if headers:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            if isinstance(data[0], dict):
                writer.writerows(data)
            else:
                writer.writerows([dict(zip(headers, row)) for row in data])
        else:
            writer = csv.writer(f)
            writer.writerows(data)
    colored_print(f"CSV file created successfully: {path}")
    return path

def create_json_file(path, data):
    colored_print(f"Creating JSON file: {path}")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    colored_print(f"JSON file created successfully: {path}")
    return path

def create_image_file(path, size=(512, 512), color=(255, 0, 0), library="pillow"):
    colored_print(f"Creating image file: {path}")
    if library.lower() == "pillow":
        image = Image.new('RGB', size, color)
        image.save(path)
    elif library.lower() == "imagemagick" and WAND_AVAILABLE:
        with WandImage(width=size[0], height=size[1], background=color) as img:
            img.save(filename=path)
    else:
        raise ValueError(f"Unsupported image library: {library}")
    colored_print(f"Image file created successfully: {path}")
    return path

def create_file(path, content="", file_type="text", image_library="pillow"):
    colored_print(f"Creating file: {path}, Type: {file_type}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if file_type.lower() in ["text", "txt"]:
        return create_text_file(path, content)
    elif file_type.lower() == "csv":
        return create_csv_file(path, content)
    elif file_type.lower() == "json":
        return create_json_file(path, content)
    elif file_type.lower() == "image":
        size = (512, 512)  # Default size
        color = (255, 0, 0)  # Default color (red)
        if isinstance(content, tuple) and len(content) == 2:
            size = content
        elif isinstance(content, tuple) and len(content) == 3:
            color = content
        return create_image_file(path, size, color, image_library)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")