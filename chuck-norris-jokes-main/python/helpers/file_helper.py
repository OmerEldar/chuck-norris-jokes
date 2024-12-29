import json
from typing import Dict, Any

class FileError(Exception):
    """Custom exception for file handling errors"""
    pass

class FileHelper:
    @staticmethod
    def read_json_file(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileError(f"File not found: {file_path}")
        except json.JSONDecodeError:
            raise FileError(f"Invalid JSON format in file: {file_path}")
        except Exception as e:
            raise FileError(f"Error reading file {file_path}: {str(e)}")