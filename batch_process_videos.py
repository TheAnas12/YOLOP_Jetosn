#!/usr/bin/env python3
"""
Batch Process Multiple Videos with YOLOP on Jetson Nano 2GB
Processes all .mp4 files in a directory with the naming convention:
Input:  {video_name}.mp4
Output: detected_{video_name}.mp4
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_video_files(input_dir):
    """Get all .mp4 files from input directory"""
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"✗ Input directory not found: {input_dir}")
        return []
    
    videos = sorted(input_path.glob('*.mp4'))
    return videos


def process_batch(input_dir, output_dir, weights_path, img_size, conf_thres, iou_thres, device, use_half):
    """Process all videos in input directory"""
    
    videos = get_video_files(input_dir)
    
    if not videos:
        print(f"✗ No .mp4 files found in: {input_dir}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Batch Processing YOLOP Videos")
    print(f"{'='*60}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Total videos: {len(videos)}")
    print(f"{'='*60}\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check for already processed videos
    existing = set()
    for output_file in Path(output_dir).glob('detected_*.mp4'):
        existing.add(output_file.name)
    
    if existing:
        print(f"Found {len(existing)} already processed videos:")
        for f in sorted(existing):
            print(f"  ✓ {f}")
        print()
    
    # Process each video
    failed_videos = []
    processed_count = 0
    
    for idx, video_path in enumerate(videos, 1):
        output_filename = f"detected_{video_path.stem}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # Skip if already processed
        if output_filename in existing:
            print(f"[{idx}/{len(videos)}] SKIP: {video_path.name}")
            print(f"  → Already exists: {output_filename}\n")
            continue
        
        print(f"[{idx}/{len(videos)}] Processing: {video_path.name}")
        
        # Build command
        cmd = [
            'python3',
            'process_video_jetson.py',
            '--video', str(video_path),
            '--weights', weights_path,
            '--output-dir', output_dir,
            '--img-size', str(img_size),
            '--conf-thres', str(conf_thres),
            '--iou-thres', str(iou_thres),
            '--device', device,
        ]
        
        if use_half:
            cmd.append('--half')
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            processed_count += 1
            print()
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to process: {video_path.name}\n")
            failed_videos.append(video_path.name)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Processing Complete!")
    print(f"{'='*60}")
    print(f"Successfully processed: {processed_count}/{len(videos)}")
    
    if failed_videos:
        print(f"Failed videos ({len(failed_videos)}):")
        for name in failed_videos:
            print(f"  ✗ {name}")
        return False
    
    print(f"\nAll videos processed successfully!")
    print(f"Output directory: {output_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Batch Process Multiple Videos with YOLOP for Jetson Nano 2GB'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        required=True,
        help='Input directory containing .mp4 files'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='videos/output',
        help='Output directory for processed videos'
    )
    parser.add_argument(
        '--weights',
        type=str,
        default='weights/End-to-end.pth',
        help='Path to model weights'
    )
    parser.add_argument(
        '--img-size',
        type=int,
        default=640,
        help='Inference image size (pixels)'
    )
    parser.add_argument(
        '--conf-thres',
        type=float,
        default=0.25,
        help='Object confidence threshold'
    )
    parser.add_argument(
        '--iou-thres',
        type=float,
        default=0.45,
        help='IOU threshold for NMS'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='cpu',
        help='Device: cuda or cpu'
    )
    parser.add_argument(
        '--half',
        action='store_true',
        help='Use half precision (FP16) if available'
    )
    
    args = parser.parse_args()
    
    # Process batch
    success = process_batch(
        args.input_dir,
        args.output_dir,
        args.weights,
        args.img_size,
        args.conf_thres,
        args.iou_thres,
        args.device,
        args.half
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
