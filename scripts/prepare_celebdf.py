"""
Prepare Celeb-DF Dataset Script
Organizes Celeb-DF videos into train/validation/test splits
"""

import os
import shutil
import random
from pathlib import Path

def organize_celebdf_dataset(celebdf_dir, output_dir, train_ratio=0.7, val_ratio=0.15):
    """
    Organize Celeb-DF dataset into train/validation/test splits
    
    Args:
        celebdf_dir: Path to Celeb-DF-v1 directory
        output_dir: Path to output organized dataset
        train_ratio: Ratio for training set (default 0.7)
        val_ratio: Ratio for validation set (default 0.15)
        test_ratio: Remaining ratio for test set (default 0.15)
    """
    
    print("=" * 60)
    print("CELEB-DF DATASET PREPARATION")
    print("=" * 60)
    
    # Create output directories
    splits = ['train', 'validation', 'test']
    classes = ['real', 'fake']
    
    print("\n📁 Creating directory structure...")
    for split in splits:
        for cls in classes:
            dir_path = os.path.join(output_dir, split, cls)
            os.makedirs(dir_path, exist_ok=True)
            print(f"   Created: {dir_path}")
    
    # Collect real videos
    print("\n📹 Collecting real videos...")
    real_videos = []
    
    # Celeb-real videos
    celeb_real_dir = os.path.join(celebdf_dir, 'Celeb-real')
    if os.path.exists(celeb_real_dir):
        for filename in os.listdir(celeb_real_dir):
            if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                real_videos.append(os.path.join(celeb_real_dir, filename))
        print(f"   Found {len(real_videos)} videos in Celeb-real/")
    else:
        print(f"   ⚠️  Warning: {celeb_real_dir} not found!")
    
    # YouTube-real videos
    youtube_real_dir = os.path.join(celebdf_dir, 'YouTube-real')
    if os.path.exists(youtube_real_dir):
        youtube_count = 0
        for filename in os.listdir(youtube_real_dir):
            if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                real_videos.append(os.path.join(youtube_real_dir, filename))
                youtube_count += 1
        print(f"   Found {youtube_count} videos in YouTube-real/")
    else:
        print(f"   ⚠️  Warning: {youtube_real_dir} not found!")
    
    print(f"   ✅ Total real videos: {len(real_videos)}")
    
    # Collect fake videos
    print("\n🎭 Collecting fake videos...")
    fake_videos = []
    
    celeb_synthesis_dir = os.path.join(celebdf_dir, 'Celeb-synthesis')
    if os.path.exists(celeb_synthesis_dir):
        for filename in os.listdir(celeb_synthesis_dir):
            if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                fake_videos.append(os.path.join(celeb_synthesis_dir, filename))
        print(f"   Found {len(fake_videos)} videos in Celeb-synthesis/")
    else:
        print(f"   ⚠️  Warning: {celeb_synthesis_dir} not found!")
    
    print(f"   ✅ Total fake videos: {len(fake_videos)}")
    
    # Check if we have videos
    if len(real_videos) == 0 and len(fake_videos) == 0:
        print("\n❌ ERROR: No videos found!")
        print("   Please check that your Celeb-DF-v1 directory contains:")
        print("   - Celeb-real/")
        print("   - Celeb-synthesis/")
        print("   - YouTube-real/")
        return
    
    # Shuffle videos
    print("\n🔀 Shuffling videos...")
    random.seed(42)  # For reproducibility
    random.shuffle(real_videos)
    random.shuffle(fake_videos)
    
    # Split videos
    def split_videos(videos, train_ratio, val_ratio):
        total = len(videos)
        train_end = int(total * train_ratio)
        val_end = int(total * (train_ratio + val_ratio))
        
        return {
            'train': videos[:train_end],
            'validation': videos[train_end:val_end],
            'test': videos[val_end:]
        }
    
    real_splits = split_videos(real_videos, train_ratio, val_ratio)
    fake_splits = split_videos(fake_videos, train_ratio, val_ratio)
    
    print(f"\n📊 Dataset Split:")
    print(f"   Real videos:")
    print(f"      Train:      {len(real_splits['train'])} ({train_ratio*100:.0f}%)")
    print(f"      Validation: {len(real_splits['validation'])} ({val_ratio*100:.0f}%)")
    print(f"      Test:       {len(real_splits['test'])} ({(1-train_ratio-val_ratio)*100:.0f}%)")
    print(f"   Fake videos:")
    print(f"      Train:      {len(fake_splits['train'])} ({train_ratio*100:.0f}%)")
    print(f"      Validation: {len(fake_splits['validation'])} ({val_ratio*100:.0f}%)")
    print(f"      Test:       {len(fake_splits['test'])} ({(1-train_ratio-val_ratio)*100:.0f}%)")
    
    # Copy videos to organized structure
    print("\n📦 Copying videos to organized structure...")
    
    for split in splits:
        print(f"\n   Processing {split} set...")
        
        # Copy real videos
        for i, video_path in enumerate(real_splits[split], 1):
            filename = os.path.basename(video_path)
            dest_path = os.path.join(output_dir, split, 'real', filename)
            shutil.copy2(video_path, dest_path)
            if i % 10 == 0 or i == len(real_splits[split]):
                print(f"      Real: {i}/{len(real_splits[split])} videos copied", end='\r')
        print(f"      ✅ Real: {len(real_splits[split])} videos copied")
        
        # Copy fake videos
        for i, video_path in enumerate(fake_splits[split], 1):
            filename = os.path.basename(video_path)
            dest_path = os.path.join(output_dir, split, 'fake', filename)
            shutil.copy2(video_path, dest_path)
            if i % 10 == 0 or i == len(fake_splits[split]):
                print(f"      Fake: {i}/{len(fake_splits[split])} videos copied", end='\r')
        print(f"      ✅ Fake: {len(fake_splits[split])} videos copied")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ DATASET PREPARATION COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output directory: {output_dir}")
    print(f"\n📊 Final Statistics:")
    print(f"   Total videos: {len(real_videos) + len(fake_videos)}")
    print(f"   Real videos:  {len(real_videos)}")
    print(f"   Fake videos:  {len(fake_videos)}")
    print(f"\n   Train set:      {len(real_splits['train']) + len(fake_splits['train'])} videos")
    print(f"   Validation set: {len(real_splits['validation']) + len(fake_splits['validation'])} videos")
    print(f"   Test set:       {len(real_splits['test']) + len(fake_splits['test'])} videos")
    print("\n✨ Ready for frame extraction! Run data_preprocessing.py next.")
    print("=" * 60)

def verify_dataset(celebdf_dir):
    """Verify that Celeb-DF dataset exists and has correct structure"""
    print("\n🔍 Verifying Celeb-DF dataset...")
    
    if not os.path.exists(celebdf_dir):
        print(f"   ❌ ERROR: Directory not found: {celebdf_dir}")
        return False
    
    required_dirs = ['Celeb-real', 'Celeb-synthesis', 'YouTube-real']
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = os.path.join(celebdf_dir, dir_name)
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) 
                            if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))])
            print(f"   ✅ {dir_name}/ found ({file_count} videos)")
        else:
            print(f"   ⚠️  {dir_name}/ not found")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"\n   ⚠️  Warning: Missing directories: {', '.join(missing_dirs)}")
        print("   The script will continue but may have limited data.")
    
    return True

if __name__ == "__main__":
    # Configuration
    CELEBDF_DIR = "../Celeb-DF-v1"  # Change this to your Celeb-DF location
    OUTPUT_DIR = "../organized_celebdf"
    
    print("\n" + "=" * 60)
    print("CELEB-DF DATASET ORGANIZATION SCRIPT")
    print("=" * 60)
    print(f"\nSource: {CELEBDF_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    
    # Verify dataset exists
    if not verify_dataset(CELEBDF_DIR):
        print("\n❌ Please update CELEBDF_DIR to point to your Celeb-DF-v1 directory")
        print("   Edit this file and change the CELEBDF_DIR variable")
        exit(1)
    
    # Ask for confirmation
    print("\n⚠️  This will copy all videos to a new organized structure.")
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Cancelled by user")
        exit(0)
    
    # Organize dataset
    try:
        organize_celebdf_dataset(
            celebdf_dir=CELEBDF_DIR,
            output_dir=OUTPUT_DIR,
            train_ratio=0.7,
            val_ratio=0.15
        )
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n✅ Script completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Review the organized dataset in:", OUTPUT_DIR)
    print("   2. Run data_preprocessing.py to extract frames")
    print("   3. Run train_model.py to train the model")