import os
import numpy as np
from tensorflow import keras
from tensorflow.keras.models import load_model

def load_trained_model(model_path):
    """Load trained CNN model"""
    try:
        if not os.path.exists(model_path):
            return None, f"Model not found at {model_path}"
        
        model = load_model(model_path)
        return model, None
    
    except Exception as e:
        return None, str(e)

def save_model(model, model_path):
    """Save trained model"""
    try:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model.save(model_path)
        return True, None
    except Exception as e:
        return False, str(e)

def predict_single(model, image_array):
    """
    Make prediction on single image
    
    Args:
        model: Trained Keras model
        image_array: Preprocessed image array
    
    Returns:
        tuple: (prediction, confidence)
    """
    try:
        # Add batch dimension
        if len(image_array.shape) == 3:
            image_array = np.expand_dims(image_array, axis=0)
        
        # Make prediction
        prediction = model.predict(image_array, verbose=0)
        
        # Get confidence (assuming binary classification)
        confidence = float(prediction[0][0])
        
        # Determine label (assuming 0=real, 1=fake)
        if confidence > 0.5:
            label = 'fake'
        else:
            label = 'real'
            confidence = 1 - confidence
        
        return label, confidence * 100
    
    except Exception as e:
        return None, str(e)

def predict_batch(model, image_arrays):
    """
    Make predictions on multiple images
    
    Args:
        model: Trained Keras model
        image_arrays: List of preprocessed image arrays
    
    Returns:
        list: List of (prediction, confidence) tuples
    """
    try:
        # Stack images
        batch = np.array(image_arrays)
        
        # Make predictions
        predictions = model.predict(batch, verbose=0)
        
        results = []
        for pred in predictions:
            confidence = float(pred[0])
            
            if confidence > 0.5:
                label = 'fake'
            else:
                label = 'real'
                confidence = 1 - confidence
            
            results.append((label, confidence * 100))
        
        return results
    
    except Exception as e:
        print(f"Error in batch prediction: {e}")
        return None

def aggregate_video_predictions(frame_predictions):
    """
    Aggregate predictions from multiple video frames
    
    Args:
        frame_predictions: List of (label, confidence) tuples
    
    Returns:
        tuple: (final_label, average_confidence)
    """
    if not frame_predictions:
        return None, None
    
    # Count fake predictions
    fake_count = sum(1 for label, _ in frame_predictions if label == 'fake')
    total = len(frame_predictions)
    
    # Majority voting
    if fake_count > total / 2:
        final_label = 'fake'
        # Average confidence of fake predictions
        fake_confidences = [conf for label, conf in frame_predictions if label == 'fake']
        avg_confidence = np.mean(fake_confidences)
    else:
        final_label = 'real'
        # Average confidence of real predictions
        real_confidences = [conf for label, conf in frame_predictions if label == 'real']
        avg_confidence = np.mean(real_confidences)
    
    return final_label, avg_confidence