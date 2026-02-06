import cv2
import numpy as np
import os

def extract_frames(video_path, num_frames=10, output_dir=None):
    """
    Extract frames from video
    
    Args:
        video_path: Path to video file
        num_frames: Number of frames to extract
        output_dir: Directory to save frames (optional)
    
    Returns:
        list: List of frame arrays or paths
    """
    try:
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None, "Could not open video file"
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Calculate frame indices to extract
        if total_frames < num_frames:
            frame_indices = list(range(total_frames))
        else:
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        frames = []
        
        for idx in frame_indices:
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                if output_dir:
                    # Save frame to file
                    frame_path = os.path.join(output_dir, f"frame_{idx}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frames.append(frame_path)
                else:
                    # Keep frame in memory
                    frames.append(frame)
        
        cap.release()
        
        return frames, None
    
    except Exception as e:
        return None, str(e)

def get_video_info(video_path):
    """Get video information"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        info = {
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info
    
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def preprocess_frame(frame, target_size=(224, 224)):
    """
    Preprocess frame for model input
    
    Args:
        frame: Input frame (numpy array)
        target_size: Target size (width, height)
    
    Returns:
        Preprocessed frame
    """
    # Resize
    frame = cv2.resize(frame, target_size)
    
    # Convert BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Normalize to [0, 1]
    frame = frame.astype(np.float32) / 255.0
    
    return frame