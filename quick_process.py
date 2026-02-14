#!/usr/bin/env python3
"""
Quick Video Processing Script for YOLOP on Jetson Nano 2GB
Simplified interface for processing videos: {video_name}.mp4 → detected_{video_name}.mp4
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}\n")


def check_prerequisites():
    """Check if prerequisites are met"""
    print_header("Checking Prerequisites")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")
    else:
        print(f"✓ Python {sys.version.split()[0]}")
    
    # Check weights
    if not Path('weights/End-to-end.pth').exists():
        issues.append("Model weights not found: weights/End-to-end.pth")
    else:
        weight_size = Path('weights/End-to-end.pth').stat().st_size / (1024*1024)
        print(f"✓ Model weights found ({weight_size:.1f} MB)")
    
    # Check required directories
    for dir_name in ['lib', 'tools', 'weights']:
        if not Path(dir_name).exists():
            issues.append(f"Directory not found: {dir_name}")
        else:
            print(f"✓ Directory found: {dir_name}/")
    
    # Create output directory if not exists
    Path('videos/output').mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: videos/output/")
    
    if issues:
        print("\n⚠ Issues found:")
        for issue in issues:
            print(f"  ✗ {issue}")
        return False
    
    print("\n✓ All prerequisites met!")
    return True


def list_input_videos():
    """List available input videos"""
    input_dir = Path('videos/input')
    input_dir.mkdir(parents=True, exist_ok=True)
    
    videos = sorted(input_dir.glob('*.mp4'))
    return videos


def process_video_simple(video_path, device='cpu', fast_mode=False):
    """Process single video with simplified interface"""
    
    output_filename = f"detected_{video_path.stem}.mp4"
    output_path = os.path.join('videos/output', output_filename)
    
    print_header(f"Processing: {video_path.name}")
    print(f"Input:  {video_path}")
    print(f"Output: {output_path}")
    print()
    
    cmd = [
        'python3',
        'process_video_jetson.py',
        '--video', str(video_path),
        '--weights', 'weights/End-to-end.pth',
        '--output-dir', 'videos/output',
    ]
    
    if fast_mode:
        print("⚡ Fast mode: Using img_size=416")
        cmd.extend(['--img-size', '416'])
    
    if device != 'cpu':
        cmd.extend(['--device', device])
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print_header("✓ Processing Complete")
            print(f"Output saved: {output_path}")
            return True
    except subprocess.CalledProcessError as e:
        print_header("✗ Processing Failed")
        return False
    
    return False


def interactive_mode():
    """Interactive selection mode"""
    videos = list_input_videos()
    
    if not videos:
        print("\n✗ No input videos found in: videos/input/")
        print("\nTo get started:")
        print("  1. Create directory: mkdir -p videos/input")
        print("  2. Copy your video: cp your_video.mp4 videos/input/")
        print("  3. Run this script again")
        return False
    
    print_header("Available Videos")
    for idx, video in enumerate(videos, 1):
        size_mb = video.stat().st_size / (1024*1024)
        print(f"  {idx}. {video.name} ({size_mb:.1f} MB)")
        
        # Check if already processed
        output_file = Path(f"videos/output/detected_{video.stem}.mp4")
        if output_file.exists():
            print(f"     → ✓ Already processed: detected_{video.stem}.mp4")
    
    print()
    choice = input("Select video(s) to process [1,2,3 or 'all']: ").strip()
    
    if choice.lower() == 'all':
        selected = videos
    else:
        try:
            indices = [int(x.strip())-1 for x in choice.split(',')]
            selected = [videos[i] for i in indices if 0 <= i < len(videos)]
        except:
            print("✗ Invalid selection")
            return False
    
    if not selected:
        print("✗ No videos selected")
        return False
    
    # Ask for device
    print("\nDevice options:")
    print("  1. CPU (slower but reliable)")
    print("  2. GPU/CUDA (faster if available)")
    device_choice = input("Select device [1/2, default=1]: ").strip() or "1"
    device = 'cuda:0' if device_choice == '2' else 'cpu'
    
    # Ask for speed
    print("\nProcessing mode:")
    print("  1. Balanced (medium speed, high accuracy)")
    print("  2. Fast (low memory, good for Jetson Nano)")
    speed_choice = input("Select mode [1/2, default=1]: ").strip() or "1"
    fast_mode = speed_choice == '2'
    
    # Process videos
    success_count = 0
    for video in selected:
        if process_video_simple(video, device=device, fast_mode=fast_mode):
            success_count += 1
        print()
    
    print_header("Summary")
    print(f"Successfully processed: {success_count}/{len(selected)}")
    
    if success_count == len(selected):
        print("\n✓ All done! Check videos/output/ for results.")
        return True
    else:
        print(f"\n⚠ {len(selected)-success_count} video(s) failed processing")
        return False


def command_line_mode(args):
    """Process single video from command line"""
    video_path = Path(args.video)
    
    if not video_path.exists():
        print(f"✗ Video not found: {args.video}")
        return False
    
    device = 'cuda:0' if args.gpu else 'cpu'
    return process_video_simple(video_path, device=device, fast_mode=args.fast)


def main():
    parser = argparse.ArgumentParser(
        description='Quick YOLOP Video Processor for Jetson Nano 2GB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive mode
  %(prog)s -v videos/input/test.mp4 # Process single video
  %(prog)s -v videos/input/test.mp4 --fast  # Fast mode
  %(prog)s -v videos/input/test.mp4 --gpu   # Use GPU
        """
    )
    
    parser.add_argument(
        '-v', '--video',
        help='Video file to process'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Use faster inference (lower accuracy, img_size=416)'
    )
    parser.add_argument(
        '--gpu',
        action='store_true',
        help='Use GPU for inference (default: CPU)'
    )
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Please install prerequisites before running.")
        sys.exit(1)
    
    # Process
    if args.video:
        # Command-line mode
        success = command_line_mode(args)
    else:
        # Interactive mode
        success = interactive_mode()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
