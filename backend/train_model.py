"""
CNN Model Training Script for Deepfake Detection
Uses preprocessed Celeb-DF dataset
"""

import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

def create_cnn_model(input_shape=(224, 224, 3)):
    """
    Create CNN model for deepfake detection
    
    Architecture:
    - Multiple convolutional layers with batch normalization
    - Max pooling layers
    - Dropout for regularization
    - Dense layers for classification
    """
    
    model = models.Sequential([
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 4
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Binary classification
    ])
    
    return model

def plot_training_history(history, save_path='training_history.png'):
    """Plot training history"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy
    ax1.plot(history.history['accuracy'], label='Train Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Loss
    ax2.plot(history.history['loss'], label='Train Loss')
    ax2.plot(history.history['val_loss'], label='Val Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Training history plot saved to {save_path}")

def train_model(data_dir, model_save_path, epochs=50, batch_size=32):
    """
    Train the deepfake detection model
    
    Args:
        data_dir: Directory containing train/validation/test folders
        model_save_path: Path to save trained model
        epochs: Number of training epochs
        batch_size: Batch size
    """
    
    print("=" * 50)
    print("DEEPFAKE DETECTION MODEL TRAINING")
    print("=" * 50)
    
    # Check if dataset exists
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'validation')
    
    if not os.path.exists(train_dir):
        print(f"Error: Training data not found at {train_dir}")
        print("Please run data_preprocessing.py first!")
        return
    
    # Data generators with augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load data
    print("\nLoading training data...")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        shuffle=True
    )
    
    print("Loading validation data...")
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        shuffle=False
    )
    
    print(f"\nTraining samples: {train_generator.samples}")
    print(f"Validation samples: {val_generator.samples}")
    print(f"Classes: {train_generator.class_indices}")
    
    # Create model
    print("\nCreating CNN model...")
    model = create_cnn_model()
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    print("\nModel Summary:")
    model.summary()
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            model_save_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train model
    print("\nStarting training...")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print("-" * 50)
    
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    model.save(model_save_path)
    print(f"\n✓ Model saved to {model_save_path}")
    
    # Plot training history
    plot_training_history(history, 'training_history.png')
    
    # Evaluate on validation set
    print("\nEvaluating model on validation set...")
    val_loss, val_accuracy, val_precision, val_recall = model.evaluate(val_generator, verbose=0)
    
    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)
    print(f"Validation Accuracy: {val_accuracy*100:.2f}%")
    print(f"Validation Precision: {val_precision*100:.2f}%")
    print(f"Validation Recall: {val_recall*100:.2f}%")
    print(f"Validation Loss: {val_loss:.4f}")
    
    return model, history

if __name__ == "__main__":
    # Configuration
    DATA_DIR = "../processed_dataset"
    MODEL_SAVE_PATH = "ml_models/cnn_model.h5"
    EPOCHS = 50
    BATCH_SIZE = 32
    
    # Create ml_models directory
    os.makedirs("ml_models", exist_ok=True)
    
    # Check if processed dataset exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: Processed dataset not found at {DATA_DIR}")
        print("Please run data_preprocessing.py first!")
        print("\nSteps:")
        print("1. Run: python data_preprocessing.py")
        print("2. Then run: python train_model.py")
        exit(1)
    
    # Train model
    model, history = train_model(
        data_dir=DATA_DIR,
        model_save_path=MODEL_SAVE_PATH,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE
    )
    
    print("\n✓ Training complete! Model ready for inference.")