import os
import zipfile
from pathlib import Path

def zip_files(file_paths, zip_path):
    """
    Zip the specified files into a new zip file.
    """
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, Path(file).name)
    return zip_path

def unzip_file(zip_path, extract_to):
    """
    Unzip the specified zip file to the given directory.
    """
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(path=extract_to)
    return extract_to

def preview_zip_changes(root_path, files_to_zip, zip_name):
    """
    Preview zip operation changes.
    """
    zip_path = os.path.join(root_path, zip_name)
    return [("zip", (files_to_zip, zip_path))]

def preview_unzip_changes(zip_path, extract_to):
    """
    Preview unzip operation changes.
    """
    return [("unzip", (zip_path, extract_to))]

def execute_zip_changes(change):
    """
    Execute zip operation.
    """
    files_to_zip, zip_path = change[1]
    zip_files(files_to_zip, zip_path)
    print(f"Created zip file: {os.path.basename(zip_path)}")

def execute_unzip_changes(change):
    """
    Execute unzip operation.
    """
    zip_path, extract_to = change[1]
    unzip_file(zip_path, extract_to)
    print(f"Extracted: {os.path.basename(zip_path)} to {extract_to}")