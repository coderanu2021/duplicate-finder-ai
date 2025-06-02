import os
import shutil
import hashlib
import magic
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class FileUtils:
    @staticmethod
    def calculate_file_hash(file_path: str, hash_type: str = 'md5') -> str:
        """Calculate the hash of a file."""
        hash_func = getattr(hashlib, hash_type)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Get the MIME type of a file."""
        return magic.from_file(file_path, mime=True)

    @staticmethod
    def get_file_metadata(file_path: str) -> Dict:
        """Get basic metadata about a file."""
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'type': FileUtils.get_file_type(file_path)
        }

    @staticmethod
    def safe_move_file(source: str, destination: str) -> bool:
        """Safely move a file to a new location."""
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # If destination file exists, add timestamp to filename
            if os.path.exists(destination):
                base, ext = os.path.splitext(destination)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                destination = f"{base}_{timestamp}{ext}"
            
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"Error moving file {source}: {str(e)}")
            return False

    @staticmethod
    def list_files(directory: str, recursive: bool = True) -> List[str]:
        """List all files in a directory."""
        files = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            files = [os.path.join(directory, f) for f in os.listdir(directory)
                    if os.path.isfile(os.path.join(directory, f))]
        return files

    @staticmethod
    def create_directory(path: str) -> bool:
        """Create a directory if it doesn't exist."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {str(e)}")
            return False

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get the file extension."""
        return os.path.splitext(file_path)[1].lower()

    @staticmethod
    def is_binary_file(file_path: str) -> bool:
        """Check if a file is binary."""
        mime = FileUtils.get_file_type(file_path)
        return not mime.startswith('text/') 