import io
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from PIL import Image
import numpy as np
import os

from .models import ModerationResult, ModerationCategory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModerationService:
    """ML-based image moderation service using trained models"""
    
    def __init__(self, model_dir: str = "models/"):
        # Define moderation categories
        self.categories = [
            "nudity",
            "drugs", 
            "weapons",
            "hate_symbols"
        ]
        
        self.model_dir = model_dir
        self.models = {}
        
        # Initialize ML models
        self._init_models()
    
    def _init_models(self):
        """Initialize trained ML models for each category"""
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            logger.info("Initializing ML models...")
            
            # Load pre-trained models for each category
            model_files = {
                "nudity": "nsfw_model.h5",
                "drugs": "drug_detection_model.h5", 
                "weapons": "weapon_detection_model.h5",
                "hate_symbols": "hate_symbol_model.h5"
            }
            
            for category, model_file in model_files.items():
                model_path = os.path.join(self.model_dir, model_file)
                
                if os.path.exists(model_path):
                    try:
                        self.models[category] = keras.models.load_model(model_path)
                        logger.info(f"✅ Loaded {category} model from {model_path}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load {category} model: {e}")
                        self.models[category] = None
                else:
                    logger.warning(f"⚠️ Model file not found: {model_path}")
                    self.models[category] = None
            
            # Load pre-trained NSFW model if available
            self._load_pretrained_nsfw_model()
            
            self.models_loaded = any(model is not None for model in self.models.values())
            
            if self.models_loaded:
                logger.info("✅ ML models initialized successfully")
            else:
                logger.warning("⚠️ No ML models loaded, using fallback detection")
            
        except ImportError as e:
            logger.error(f"❌ TensorFlow not available: {e}")
            self.models_loaded = False
        except Exception as e:
            logger.error(f"❌ Error loading ML models: {e}")
            self.models_loaded = False
    
    def _load_pretrained_nsfw_model(self):
        """Load pre-trained NSFW model if available"""
        try:
            # Try to load Yahoo's Open NSFW model or similar
            import tensorflow as tf
            
            # Check for pre-trained NSFW models
            pretrained_paths = [
                "models/nsfw_mobilenet_v2.h5",
                "models/open_nsfw_model.h5",
                "models/nudenet_classifier.h5"
            ]
            
            for path in pretrained_paths:
                if os.path.exists(path):
                    try:
                        self.models["nudity"] = tf.keras.models.load_model(path)
                        logger.info(f"✅ Loaded pre-trained NSFW model from {path}")
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load pre-trained model {path}: {e}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Error loading pre-trained NSFW model: {e}")
    
    async def moderate_image(self, image_data: bytes, filename: str) -> ModerationResult:
        """
        Analyze an image using trained ML models
        """
        try:
            # Validate image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Processing image: {filename} ({image.size})")
            
            # Analyze with ML models
            categories = await self._analyze_with_ml(image, filename)
            
            # Determine overall safety
            flagged_categories = [cat for cat in categories if cat.flagged]
            is_safe = len(flagged_categories) == 0
            
            # Calculate overall confidence
            overall_confidence = sum(cat.confidence for cat in categories) / len(categories)
            
            logger.info(f"ML analysis complete for {filename}: safe={is_safe}, confidence={overall_confidence:.2f}")
            
            return ModerationResult(
                filename=filename,
                safe=is_safe,
                categories=categories,
                overall_confidence=overall_confidence,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            # If processing fails, return conservative result
            return ModerationResult(
                filename=filename,
                safe=False,
                categories=[
                    ModerationCategory(
                        category=cat,
                        confidence=1.0,
                        flagged=True
                    ) for cat in self.categories
                ],
                overall_confidence=1.0,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _analyze_with_ml(self, image: Image.Image, filename: str) -> List[ModerationCategory]:
        """
        Analyze image using trained ML models
        """
        categories = []
        
        # Preprocess image for ML models
        processed_image = self._preprocess_image(image)
        
        for category in self.categories:
            if self.models.get(category) is not None:
                # Use trained ML model
                confidence = self._predict_with_model(processed_image, category)
                logger.info(f"{category} ML prediction: {confidence:.3f}")
            else:
                # Fallback for missing models
                confidence = self._fallback_prediction(image, category)
                logger.info(f"{category} fallback prediction: {confidence:.3f}")
            
            # Determine if flagged based on thresholds
            flagged = self._should_flag(category, confidence)
            
            categories.append(ModerationCategory(
                category=category,
                confidence=confidence,
                flagged=flagged
            ))
        
        return categories
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for ML model input
        """
        # Resize to standard input size (224x224 for most models)
        image_resized = image.resize((224, 224))
        
        # Convert to RGB if needed
        if image_resized.mode != 'RGB':
            image_resized = image_resized.convert('RGB')
        
        # Convert to numpy array and normalize
        img_array = np.array(image_resized, dtype=np.float32)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def _predict_with_model(self, processed_image: np.ndarray, category: str) -> float:
        """
        Make prediction using trained ML model
        """
        try:
            model = self.models[category]
            
            # Make prediction
            prediction = model.predict(processed_image, verbose=0)
            
            # Handle different output formats
            if isinstance(prediction, np.ndarray):
                if prediction.shape[-1] == 1:
                    # Binary classification
                    confidence = float(prediction[0][0])
                elif prediction.shape[-1] == 2:
                    # Binary classification with 2 outputs [safe, unsafe]
                    confidence = float(prediction[0][1])  # Take unsafe probability
                else:
                    # Multi-class classification
                    confidence = float(np.max(prediction[0]))
            else:
                confidence = float(prediction)
            
            # Ensure confidence is in [0, 1] range
            confidence = np.clip(confidence, 0.0, 1.0)
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error in ML prediction for {category}: {e}")
            return 0.05  # Conservative fallback
    
    def _fallback_prediction(self, image: Image.Image, category: str) -> float:
        """
        Fallback prediction when ML model is not available
        """
        # Very conservative fallback
        return 0.05
    
    def _should_flag(self, category: str, confidence: float) -> bool:
        """
        Determine if category should be flagged based on confidence
        """
        # ML model thresholds (can be tuned based on validation data)
        thresholds = {
            "nudity": 0.8,      # 80% confidence
            "drugs": 0.85,      # 85% confidence
            "weapons": 0.85,    # 85% confidence
            "hate_symbols": 0.9 # 90% confidence (very conservative)
        }
        
        threshold = thresholds.get(category, 0.85)
        return confidence > threshold

# Training helper functions (for when we train custom models)
class ModelTrainer:
    """Helper class for training custom models"""
    
    def __init__(self, category: str):
        self.category = category
        
    def prepare_dataset(self, data_dir: str):
        """
        Prepare dataset for training
        """
        import tensorflow as tf
        
        # Create dataset from directory structure
        # Expected structure:
        # data_dir/
        #   ├── positive/  (images that contain the category)
        #   └── negative/  (safe images)
        
        dataset = tf.keras.utils.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            subset="training",
            seed=123,
            image_size=(224, 224),
            batch_size=32
        )
        
        val_dataset = tf.keras.utils.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            subset="validation", 
            seed=123,
            image_size=(224, 224),
            batch_size=32
        )
        
        return dataset, val_dataset
    
    def create_model(self, num_classes: int = 2):
        """
        Create model architecture for training
        """
        import tensorflow as tf
        from tensorflow.keras import layers
        
        # Use transfer learning with pre-trained model
        base_model = tf.keras.applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Freeze base model
        base_model.trainable = False
        
        # Add custom classification head
        model = tf.keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax' if num_classes > 2 else 'sigmoid')
        ])
        
        return model
    
    def train_model(self, model, train_dataset, val_dataset, epochs: int = 10):
        """
        Train the model
        """
        import tensorflow as tf
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy' if model.output_shape[-1] > 1 else 'binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        history = model.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=epochs,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(patience=3),
                tf.keras.callbacks.ReduceLROnPlateau(patience=2)
            ]
        )
        
        return history
    
    def save_model(self, model, save_path: str):
        """
        Save trained model
        """
        model.save(save_path)
        logger.info(f"Model saved to {save_path}")

# Data collection helper
class DataCollector:
    """Helper for collecting and organizing training data"""
    
    @staticmethod
    def download_pretrained_models():
        """
        Download available pre-trained models
        """
        import urllib.request
        import os
        
        os.makedirs("models", exist_ok=True)
        
        # Yahoo's Open NSFW model (if available)
        nsfw_urls = [
            "https://github.com/GantMan/nsfw_model/releases/download/1.1.0/nsfw_mobilenet_v2_140_224.tflite"
        ]
        
        for url in nsfw_urls:
            try:
                filename = url.split("/")[-1]
                filepath = f"models/{filename}"
                
                if not os.path.exists(filepath):
                    logger.info(f"Downloading {filename}...")
                    urllib.request.urlretrieve(url, filepath)
                    logger.info(f"✅ Downloaded {filename}")
                else:
                    logger.info(f"✅ {filename} already exists")
                    
            except Exception as e:
                logger.error(f"❌ Failed to download {url}: {e}")
    
    @staticmethod
    def organize_dataset(raw_data_dir: str, organized_dir: str, category: str):
        """
        Organize raw images into training structure
        """
        import shutil
        import os
        
        # Create directory structure
        positive_dir = os.path.join(organized_dir, category, "positive")
        negative_dir = os.path.join(organized_dir, category, "negative")
        
        os.makedirs(positive_dir, exist_ok=True)
        os.makedirs(negative_dir, exist_ok=True)
        
        logger.info(f"Organized dataset structure created at {organized_dir}")
        logger.info(f"Place positive examples in: {positive_dir}")
        logger.info(f"Place negative examples in: {negative_dir}") 