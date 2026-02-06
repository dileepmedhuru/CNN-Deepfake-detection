"""
Data Preprocessing Script for Celeb-DF Dataset
This script extracts frames from videos and organizes them for training
"""

import os
import cv2
import shutil
from pathlib import Path
import random

def extract_frames_from_video(video_path, output_dir, num_frames=10):
    """Extract frames from a single video"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Could not open video: {video_path}")
            return 0
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames < num_frames:
            frame_indices = list(range(total_frames))
        else:
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
        
        saved_count = 0
        video_name = Path(video_path).stem
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                frame_filename = f"{video_name}_frame_{idx}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                cv2.imwrite(frame_path, frame)
                saved_count += 1
        
        cap.release()
        return saved_count
    
    except Exception as e:
        print(f"Error processing {video_path}: {e}")
        return 0

def process_celebdf_dataset(celebdf_dir, output_dir, frames_per_video=10):
    """
    Process Celeb-DF dataset
    
    Directory structure:
    celebdf_dir/
        Celeb-real/         -> Real videos
        Celeb-synthesis/    -> Fake videos
        YouTube-real/       -> Real videos
    
    Output structure:
    output_dir/
        train/
            real/
            fake/
        validation/
            real/
            fake/
        test/
            real/
            fake/
    """
    
    print("Starting Celeb-DF dataset preprocessing...")
    
    # Create output directories
    splits = ['train', 'validation', 'test']
    classes = ['real', 'fake']
    
    for split in splits:
        for cls in classes:
            os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)
    
    # Process real videos
    print("\nProcessing real videos...")
    real_videos = []
    
    # Celeb-real
    celeb_real_dir = os.path.join(celebdf_dir, 'Celeb-real')
    if os.path.exists(celeb_real_dir):
        real_videos.extend([
            os.path.join(celeb_real_dir, f) 
            for f in os.listdir(celeb_real_dir) 
            if f.endswith(('.mp4', '.avi', '.mov'))
        ])
    
    # YouTube-real
    youtube_real_dir = os.path.join(celebdf_dir, 'YouTube-real')
    if os.path.exists(youtube_real_dir):
        real_videos.extend([
            os.path.join(youtube_real_dir, f) 
            for f in os.listdir(youtube_real_dir) 
            if f.endswith(('.mp4', '.avi', '.mov'))
        ])
    
    # Process fake videos
    print("Processing fake videos...")
    fake_videos = []
    
    celeb_synthesis_dir = os.path.join(celebdf_dir, 'Celeb-synthesis')
    if os.path.exists(celeb_synthesis_dir):
        fake_videos.extend([
            os.path.join(celeb_synthesis_dir, f) 
            for f in os.listdir(celeb_synthesis_dir) 
            if f.endswith(('.mp4', '.avi', '.mov'))
        ])
    
    # Shuffle
    random.shuffle(real_videos)
    random.shuffle(fake_videos)
    
    # Split ratios
    train_ratio = 0.7
    val_ratio = 0.15
    # test_ratio = 0.15
    
    def split_videos(videos):
        total = len(videos)
        train_end = int(total * train_ratio)
        val_end = int(total * (train_ratio + val_ratio))
        
        return {
            'train': videos[:train_end],
            'validation': videos[train_end:val_end],
            'test': videos[val_end:]
        }
    
    real_splits = split_videos(real_videos)
    fake_splits = split_videos(fake_videos)
    
    print(f"\nDataset split:")
    print(f"Real videos - Train: {len(real_splits['train'])}, Val: {len(real_splits['validation'])}, Test: {len(real_splits['test'])}")
    print(f"Fake videos - Train: {len(fake_splits['train'])}, Val: {len(fake_splits['validation'])}, Test: {len(fake_splits['test'])}")
    
    # Extract frames
    total_frames = 0
    
    for split in splits:
        print(f"\nProcessing {split} set...")
        
        # Real videos
        print(f"  Extracting frames from real videos...")
        for video_path in real_splits[split]:
            output_path = os.path.join(output_dir, split, 'real')
            frames = extract_frames_from_video(video_path, output_path, frames_per_video)
            total_frames += frames
        
        # Fake videos
        print(f"  Extracting frames from fake videos...")
        for video_path in fake_splits[split]:
            output_path = os.path.join(output_dir, split, 'fake')
            frames = extract_frames_from_video(video_path, output_path, frames_per_video)
            total_frames += frames
    
    print(f"\nPreprocessing complete!")
    print(f"Total frames extracted: {total_frames}")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    # Paths
    CELEBDF_DIR = "../Celeb-DF-v1"  # Adjust this to your dataset location
    OUTPUT_DIR = "../processed_dataset"
    
    # Check if dataset exists
    if not os.path.exists(CELEBDF_DIR):
        print(f"Error: Celeb-DF dataset not found at {CELEBDF_DIR}")
        print("Please update the CELEBDF_DIR path in this script.")
        exit(1)
    
    # Process dataset
    process_celebdf_dataset(
        celebdf_dir=CELEBDF_DIR,
        output_dir=OUTPUT_DIR,
        frames_per_video=10
    )
    
    print("\n✓ Dataset ready for training!")