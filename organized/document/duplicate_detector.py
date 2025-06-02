from typing import Dict, List, Set, Tuple
from collections import defaultdict
import os
from utils.file_utils import FileUtils
from utils.logger import Logger

class DuplicateDetector:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.file_utils = FileUtils()

    def find_duplicates(self, directory: str, hash_type: str = 'md5') -> Dict[str, List[str]]:
        """
        Find duplicate files in a directory based on file hash.
        Returns a dictionary mapping file hashes to lists of file paths.
        """
        hash_map = defaultdict(list)
        
        # Get all files in directory
        files = self.file_utils.list_files(directory)
        
        # Calculate hash for each file
        for file_path in files:
            try:
                file_hash = self.file_utils.calculate_file_hash(file_path, hash_type)
                hash_map[file_hash].append(file_path)
                
                # Log file metadata
                metadata = self.file_utils.get_file_metadata(file_path)
                self.logger.log_file_metadata(
                    file_path=file_path,
                    file_hash=file_hash,
                    file_type=metadata['type'],
                    file_size=metadata['size'],
                    last_modified=metadata['modified'],
                    created_at=metadata['created']
                )
            except Exception as e:
                self.logger.log_operation(
                    operation_type="hash_calculation",
                    source_path=file_path,
                    status="failure",
                    details=str(e)
                )
        
        # Filter out non-duplicates
        return {k: v for k, v in hash_map.items() if len(v) > 1}

    def find_similar_files(self, directory: str, similarity_threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """
        Find similar files based on content similarity.
        This is a placeholder for more advanced similarity detection.
        """
        # TODO: Implement more sophisticated similarity detection
        # For now, return empty list
        return []

    def remove_duplicates(self, duplicates: Dict[str, List[str]], 
                         keep_strategy: str = 'newest') -> List[str]:
        """
        Remove duplicate files based on the specified strategy.
        Strategies: 'newest', 'oldest', 'largest', 'smallest'
        Returns list of removed file paths.
        """
        removed_files = []
        
        for file_hash, file_paths in duplicates.items():
            if len(file_paths) <= 1:
                continue
                
            # Sort files based on strategy
            if keep_strategy == 'newest':
                sorted_files = sorted(file_paths, 
                                    key=lambda x: os.path.getmtime(x), 
                                    reverse=True)
            elif keep_strategy == 'oldest':
                sorted_files = sorted(file_paths, 
                                    key=lambda x: os.path.getmtime(x))
            elif keep_strategy == 'largest':
                sorted_files = sorted(file_paths, 
                                    key=lambda x: os.path.getsize(x), 
                                    reverse=True)
            elif keep_strategy == 'smallest':
                sorted_files = sorted(file_paths, 
                                    key=lambda x: os.path.getsize(x))
            else:
                raise ValueError(f"Unknown keep strategy: {keep_strategy}")
            
            # Keep the first file, remove the rest
            keep_file = sorted_files[0]
            for file_to_remove in sorted_files[1:]:
                try:
                    os.remove(file_to_remove)
                    removed_files.append(file_to_remove)
                    self.logger.log_operation(
                        operation_type="duplicate_removal",
                        source_path=file_to_remove,
                        status="success",
                        details=f"Kept file: {keep_file}"
                    )
                except Exception as e:
                    self.logger.log_operation(
                        operation_type="duplicate_removal",
                        source_path=file_to_remove,
                        status="failure",
                        details=str(e)
                    )
        
        return removed_files

    def analyze_duplicates(self, duplicates: Dict[str, List[str]]) -> Dict:
        """
        Analyze duplicate files and return statistics.
        """
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        total_space = sum(os.path.getsize(files[0]) * (len(files) - 1) 
                         for files in duplicates.values())
        
        return {
            'total_duplicate_groups': len(duplicates),
            'total_duplicate_files': total_duplicates,
            'potential_space_saved': total_space,
            'duplicate_types': self._get_duplicate_types(duplicates)
        }

    def _get_duplicate_types(self, duplicates: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Get count of duplicate files by type.
        """
        type_counts = defaultdict(int)
        for files in duplicates.values():
            file_type = self.file_utils.get_file_type(files[0])
            type_counts[file_type] += len(files) - 1
        return dict(type_counts) 