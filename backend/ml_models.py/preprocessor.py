import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess single image for model input
    
    Args:
        image_path: Path to image file
        target_size: Target size (width, height)
    
    Returns:
        Preprocessed image array
    """
    # Read image
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Resize
    image = cv2.resize(image, target_size)
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Normalize to [0, 1]
    image = image.astype(np.float32) / 255.0
    
    return image

def preprocess_batch(image_paths, target_size=(224, 224)):
    """
    Preprocess batch of images
    
    Args:
        image_paths: List of image file paths
        target_size: Target size (width, height)
    
    Returns:
        Numpy array of preprocessed images
    """
    images = []
    
    for path in image_paths:
        try:
            img = preprocess_image(path, target_size)
            images.append(img)
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    return np.array(images)

def create_data_generator(augment=True):
    """
    Create data generator for training
    
    Args:
        augment: Whether to apply data augmentation
    
    Returns:
        ImageDataGenerator instance
    """
    if augment:
        return ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
    else:
        return ImageDataGenerator(rescale=1./255)

def load_dataset(data_dir, target_size=(224, 224), batch_size=32, augment=True):
    """
    Load dataset using data generator
    
    Args:
        data_dir: Directory containing train/validation subdirectories
        target_size: Target image size
        batch_size: Batch size
        augment: Apply data augmentation
    
    Returns:
        Data generator
    """
    datagen = create_data_generator(augment)
    
    generator = datagen.flow_from_directory(
        data_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary',
        shuffle=True
    )
    
    return generator