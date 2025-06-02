import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity
from classifier.model import DocumentClassifier
import mimetypes

class DuplicateDetector:
    def __init__(self, model_path: str = None):
        self.classifier = DocumentClassifier()
        if model_path and Path(model_path).exists():
            self.classifier.load_state_dict(torch.load(model_path))
        self.classifier.eval()
        
    def compute_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def is_text_file(self, file_path):
        mime = mimetypes.guess_type(file_path)[0]
        return mime is not None and mime.startswith('text')

    def compute_embeddings(self, file_path):
        if self.is_text_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                return self.compute_embeddings(text)
            except Exception as e:
                print(f"Error reading text file {file_path}: {e}")
                return None
        else:
            # For binary files, return hash as embedding
            return self.compute_hash(file_path)
    
    def compute_similarity(self, file1: str, file2: str) -> float:
        """Compute similarity between two files."""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                text1 = f.read()
            with open(file2, 'r', encoding='utf-8') as f:
                text2 = f.read()
                
            embedding1 = self.compute_embeddings(text1)
            embedding2 = self.compute_embeddings(text2)
            
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error computing similarity: {str(e)}")
            return 0.0
    
    def find_duplicates(self, file_paths: List[str], similarity_threshold: float = 0.95) -> List[Tuple[str, str]]:
        """Find duplicate files based on content similarity."""
        duplicates = []
        file_embeddings = {}
        for file_path in file_paths:
            emb = self.compute_embeddings(file_path)
            if emb is not None:
                file_embeddings[file_path] = emb

        checked = set()
        file_list = list(file_embeddings.keys())
        for i in range(len(file_list)):
            for j in range(i + 1, len(file_list)):
                file1, file2 = file_list[i], file_list[j]
                emb1, emb2 = file_embeddings[file1], file_embeddings[file2]
                # If both are hashes (binary files)
                if isinstance(emb1, str) and isinstance(emb2, str):
                    if emb1 == emb2:
                        duplicates.append((file1, file2))
                # If both are embeddings (text files)
                elif not isinstance(emb1, str) and not isinstance(emb2, str):
                    similarity = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
                    if similarity >= similarity_threshold:
                        duplicates.append((file1, file2))
                # Don't compare hash to embedding (different types)
        return duplicates 