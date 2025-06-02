import os
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from PIL import Image
import torch
from transformers import AutoFeatureExtractor, AutoModel
from utils.file_utils import FileUtils
from utils.logger import Logger

class FileClassifier:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.file_utils = FileUtils()
        self.text_classifier = None
        self.image_classifier = None
        self._init_classifiers()

    def _init_classifiers(self):
        """Initialize the text and image classifiers."""
        # Text classifier pipeline
        self.text_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000)),
            ('classifier', RandomForestClassifier(n_estimators=100))
        ])

        # Image classifier (using pre-trained model)
        try:
            self.image_extractor = AutoFeatureExtractor.from_pretrained("microsoft/resnet-50")
            self.image_model = AutoModel.from_pretrained("microsoft/resnet-50")
        except Exception as e:
            self.logger.log_operation(
                operation_type="model_initialization",
                source_path="image_classifier",
                status="failure",
                details=str(e)
            )
            self.image_extractor = None
            self.image_model = None

    def classify_file(self, file_path: str) -> Dict:
        """
        Classify a file based on its content and type.
        Returns a dictionary with classification results.
        """
        file_type = self.file_utils.get_file_type(file_path)
        classification = {
            'file_path': file_path,
            'file_type': file_type,
            'category': 'unknown',
            'confidence': 0.0
        }

        try:
            if file_type.startswith('text/'):
                classification.update(self._classify_text_file(file_path))
            elif file_type.startswith('image/'):
                classification.update(self._classify_image_file(file_path))
            else:
                # Use file extension for other types
                ext = self.file_utils.get_file_extension(file_path)
                classification['category'] = self._get_category_from_extension(ext)
                classification['confidence'] = 1.0

        except Exception as e:
            self.logger.log_operation(
                operation_type="file_classification",
                source_path=file_path,
                status="failure",
                details=str(e)
            )

        return classification

    def _classify_text_file(self, file_path: str) -> Dict:
        """Classify a text file based on its content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # TODO: Implement actual text classification
            # For now, return a basic classification
            return {
                'category': 'document',
                'confidence': 0.8
            }
        except Exception as e:
            self.logger.log_operation(
                operation_type="text_classification",
                source_path=file_path,
                status="failure",
                details=str(e)
            )
            return {'category': 'unknown', 'confidence': 0.0}

    def _classify_image_file(self, file_path: str) -> Dict:
        """Classify an image file using the pre-trained model."""
        if not self.image_extractor or not self.image_model:
            return {'category': 'image', 'confidence': 0.5}

        try:
            image = Image.open(file_path)
            inputs = self.image_extractor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = self.image_model(**inputs)
            
            # TODO: Implement actual image classification
            # For now, return a basic classification
            return {
                'category': 'image',
                'confidence': 0.9
            }
        except Exception as e:
            self.logger.log_operation(
                operation_type="image_classification",
                source_path=file_path,
                status="failure",
                details=str(e)
            )
            return {'category': 'image', 'confidence': 0.5}

    def _get_category_from_extension(self, extension: str) -> str:
        """Get a basic category based on file extension."""
        extension = extension.lower()
        
        # Image extensions
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            return 'image'
        
        # Document extensions
        elif extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            return 'document'
        
        # Video extensions
        elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv']:
            return 'video'
        
        # Audio extensions
        elif extension in ['.mp3', '.wav', '.ogg', '.flac']:
            return 'audio'
        
        # Code extensions
        elif extension in ['.py', '.java', '.cpp', '.js', '.html', '.css']:
            return 'code'
        
        # Archive extensions
        elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return 'archive'
        
        else:
            return 'other'

    def train_text_classifier(self, training_data: List[Tuple[str, str]]):
        """
        Train the text classifier with provided data.
        training_data should be a list of (text, category) tuples.
        """
        try:
            texts, categories = zip(*training_data)
            self.text_classifier.fit(texts, categories)
            
            self.logger.log_operation(
                operation_type="model_training",
                source_path="text_classifier",
                status="success",
                details=f"Trained on {len(training_data)} samples"
            )
        except Exception as e:
            self.logger.log_operation(
                operation_type="model_training",
                source_path="text_classifier",
                status="failure",
                details=str(e)
            )

    def save_models(self, directory: str):
        """Save the trained models to disk."""
        try:
            os.makedirs(directory, exist_ok=True)
            
            # Save text classifier
            import joblib
            joblib.dump(self.text_classifier, os.path.join(directory, 'text_classifier.joblib'))
            
            # Save image model
            if self.image_model:
                self.image_model.save_pretrained(os.path.join(directory, 'image_model'))
                self.image_extractor.save_pretrained(os.path.join(directory, 'image_extractor'))
            
            self.logger.log_operation(
                operation_type="model_save",
                source_path=directory,
                status="success"
            )
        except Exception as e:
            self.logger.log_operation(
                operation_type="model_save",
                source_path=directory,
                status="failure",
                details=str(e)
            )

    def load_models(self, directory: str):
        """Load trained models from disk."""
        try:
            # Load text classifier
            import joblib
            self.text_classifier = joblib.load(os.path.join(directory, 'text_classifier.joblib'))
            
            # Load image model
            model_path = os.path.join(directory, 'image_model')
            if os.path.exists(model_path):
                self.image_model = AutoModel.from_pretrained(model_path)
                self.image_extractor = AutoFeatureExtractor.from_pretrained(
                    os.path.join(directory, 'image_extractor')
                )
            
            self.logger.log_operation(
                operation_type="model_load",
                source_path=directory,
                status="success"
            )
        except Exception as e:
            self.logger.log_operation(
                operation_type="model_load",
                source_path=directory,
                status="failure",
                details=str(e)
            ) 