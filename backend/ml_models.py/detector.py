import numpy as np
from tensorflow.keras.models import load_model
from ml_models.preprocessor import preprocess_image
import os

class DeepfakeDetector:
    """Deepfake detector class"""
    
    def __init__(self, model_path):
        """Initialize detector with model path"""
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
    
    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        try:
            self.model = load_model(self.model_path)
            self.is_loaded = True
            print(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def predict_image(self, image_path, threshold=0.5):
        """
        Predict if image is fake or real
        
        Args:
            image_path: Path to image file
            threshold: Classification threshold (default 0.5)
        
        Returns:
            dict: {
                'prediction': 'fake' or 'real',
                'confidence': float (0-100),
                'probability': float (0-1)
            }
        """
        if not self.is_loaded:
            self.load_model()
        
        # Preprocess image
        image = preprocess_image(image_path, target_size=(224, 224))
        image = np.expand_dims(image, axis=0)  # Add batch dimension
        
        # Make prediction
        probability = self.model.predict(image, verbose=0)[0][0]
        
        # Determine label (assuming 1=fake, 0=real)
        if probability > threshold:
            prediction = 'fake'
            confidence = probability * 100
        else:
            prediction = 'real'
            confidence = (1 - probability) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(confidence, 2),
            'probability': round(probability, 4)
        }
    
    def predict_batch(self, image_paths, threshold=0.5):
        """
        Predict multiple images
        
        Args:
            image_paths: List of image file paths
            threshold: Classification threshold
        
        Returns:
            list: List of prediction dictionaries
        """
        if not self.is_loaded:
            self.load_model()
        
        results = []
        
        for path in image_paths:
            try:
                result = self.predict_image(path, threshold)
                results.append(result)
            except Exception as e:
                results.append({
                    'prediction': 'error',
                    'confidence': 0,
                    'error': str(e)
                })
        
        return results
    
    def predict_video_frames(self, frame_paths, threshold=0.5):
        """
        Predict video by analyzing multiple frames
        
        Args:
            frame_paths: List of frame image paths
            threshold: Classification threshold
        
        Returns:
            dict: Aggregated prediction result
        """
        frame_results = self.predict_batch(frame_paths, threshold)
        
        # Count fake predictions
        fake_count = sum(1 for r in frame_results if r['prediction'] == 'fake')
        total = len(frame_results)
        
        # Majority voting
        if fake_count > total / 2:
            prediction = 'fake'
            # Average confidence of fake predictions
            confidences = [r['confidence'] for r in frame_results if r['prediction'] == 'fake']
        else:
            prediction = 'real'
            # Average confidence of real predictions
            confidences = [r['confidence'] for r in frame_results if r['prediction'] == 'real']
        
        avg_confidence = np.mean(confidences) if confidences else 0
        
        return {
            'prediction': prediction,
            'confidence': round(avg_confidence, 2),
            'frames_analyzed': total,
            'fake_frames': fake_count,
            'real_frames': total - fake_count
        }