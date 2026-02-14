# YOLOP Workflow for Jetson Nano 2GB

## Overview

This workflow enables **YOLOP (You Only Look Once for Panoptic Driving Perception)** to run efficiently on **Jetson Nano 2GB**. YOLOP is a multi-task driving perception model that simultaneously performs:

1. **Object Detection** - Detects vehicles, pedestrians, cyclists, etc.
2. **Drivable Area Segmentation** - Identifies drivable road areas
3. **Lane Detection** - Detects lane lines

### Performance Characteristics
- **Inference Speed**: ~41 FPS (on Jetson TX2, ~5-15 FPS on Jetson Nano 2GB)
- **Model Size**: ~27 MB
- **Memory Usage**: ~500MB-1GB (optimized for Jetson Nano)
- **Accuracy**: 89.2% AP (detection), 91.5% mIoU (segmentation), 70.5% F1 (lane)

## What is YOLOP?

YOLOP is an efficient multi-task neural network that handles three crucial autonomous driving tasks jointly:
- Reduces computational costs compared to single-task models
- Faster inference time while maintaining state-of-the-art performance
- Designed to work efficiently on embedded devices like Jetson platforms

**Project Structure**:
```
YOLOP/
├── lib/               # Core library code
│   ├── config/        # Configuration files
│   ├── core/          # Model inference, loss functions, metrics
│   ├── dataset/       # Dataset loading and processing
│   ├── models/        # YOLOP model architecture
│   └── utils/         # Utility functions
├── tools/             # Training/inference tools
│   ├── demo.py        # Original demo script
│   ├── train.py       # Training script
│   └── test.py        # Testing/evaluation script
├── weights/           # Pre-trained model weights
├── videos/            # Input/output videos
├── process_video_jetson.py    # Single video processor
├── batch_process_videos.py    # Batch processor
├── setup_jetson_nano.sh       # Environment setup
└── jetson_nano_config.cfg     # Optimization configuration
```

## Quick Start

### 1. Setup Environment on Jetson Nano

```bash
# Make setup script executable
chmod +x setup_jetson_nano.sh

# Run setup (requires sudo for system packages)
./setup_jetson_nano.sh

# This will:
# - Install system dependencies
# - Install PyTorch/TorchVision for ARM64
# - Install YOLOP requirements
# - Create necessary directories
```

### 2. Prepare Your Videos

Place your video files in the `videos/input/` directory:

```bash
cp your_video.mp4 videos/input/
# Files should be named: {video_name}.mp4
# Examples: street_scene.mp4, highway_drive.mp4, parking_lot.mp4
```

### 3. Download Pre-trained Weights

Download from YOLOP releases and place in `weights/`:

```bash
# Download End-to-end.pth from GitHub releases
# https://github.com/hustvl/YOLOP/releases

# Verify weights exist
ls -lh weights/End-to-end.pth  # Should show ~27 MB file
```

### 4. Process Single Video

```bash
# Process a single video
python3 process_video_jetson.py \
    --video videos/input/your_video.mp4 \
    --weights weights/End-to-end.pth \
    --output-dir videos/output

# This creates: videos/output/detected_your_video.mp4
```

### 5. Process Multiple Videos (Batch Mode)

```bash
# Process all videos in input directory
python3 batch_process_videos.py \
    --input-dir videos/input \
    --output-dir videos/output \
    --weights weights/End-to-end.pth

# This processes all .mp4 files and creates:
# - detected_video1.mp4
# - detected_video2.mp4
# - detected_video3.mp4
# (etc.)
```

## Command Line Arguments

### `process_video_jetson.py`

| Argument | Default | Description |
|----------|---------|-------------|
| `--video` | required | Input video path |
| `--weights` | `weights/End-to-end.pth` | Path to model weights |
| `--output-dir` | `videos/output` | Output directory |
| `--img-size` | 640 | Inference image size (pixels) |
| `--conf-thres` | 0.25 | Object confidence threshold (0.0-1.0) |
| `--iou-thres` | 0.45 | IOU threshold for NMS (0.0-1.0) |
| `--device` | cpu | Device: `cpu` or `cuda:0` |
| `--half` | false | Use FP16 half precision (if CUDA capable) |

**Examples**:

```bash
# Low confidence threshold (detect more objects)
python3 process_video_jetson.py \
    --video videos/input/test.mp4 \
    --conf-thres 0.1

# High confidence (only high-confidence detections)
python3 process_video_jetson.py \
    --video videos/input/test.mp4 \
    --conf-thres 0.5

# Smaller input size (faster, but less accurate)
python3 process_video_jetson.py \
    --video videos/input/test.mp4 \
    --img-size 416

# Larger input size (slower, but more accurate)
python3 process_video_jetson.py \
    --video videos/input/test.mp4 \
    --img-size 960
```

### `batch_process_videos.py`

Same arguments as `process_video_jetson.py`, except:
- Use `--input-dir` instead of `--video` to process all `.mp4` files

## Output Naming Convention

**Input**: `{video_name}.mp4`  
**Output**: `detected_{video_name}.mp4`

**Examples**:
- `street_scene.mp4` → `detected_street_scene.mp4`
- `highway_drive.mp4` → `detected_highway_drive.mp4`
- `test_video.mp4` → `detected_test_video.mp4`

All output videos are saved to the `--output-dir` (default: `videos/output/`)

## Output Format and Visualization

The output videos contain overlaid annotations:

1. **Detection Boxes**: 
   - Red boxes = vehicles/pedestrians
   - Each box shows class label and confidence score
   - Format: `[Class] [Confidence]` (e.g., "car 0.92")

2. **Drivable Area Segmentation**:
   - Green-tinted overlay = drivable road area
   - Identifies where the vehicle can safely drive

3. **Lane Detection**:
   - Yellow lines = detected lane markings
   - Helps with lane-keeping and navigation

4. **Frame Indicators**:
   - Progress bar shows processing status
   - Inference/NMS timing statistics

## Performance on Jetson Nano 2GB

### Typical Processing Times (640x640 input):

| Input Resolution | Processing Speed | Memory Usage |
|------------------|------------------|-------------|
| 480p | ~100-150 ms/frame | ~600 MB |
| 720p | ~200-300 ms/frame | ~800 MB |
| 1080p | ~400-600 ms/frame | ~1000+ MB |

### Recommended Settings:

```bash
# For Real-time Processing (30 FPS):
python3 process_video_jetson.py \
    --video videos/input/480p_video.mp4 \
    --img-size 416 \
    --conf-thres 0.3

# For Accurate Processing:
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --img-size 640 \
    --conf-thres 0.25
```

## Memory Optimization Tips

### 1. Monitor Memory Usage

```bash
# On Jetson Nano, check real-time memory:
free -h
top -b -n 1 | head -n 20
```

### 2. Increase Swap Space (if needed)

```bash
# Create 4GB swap file (takes time but helps Jetson Nano)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. Reduce Image Size

```bash
# Use smaller input size for lower memory usage
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --img-size 416  # Instead of 640

# Or even smaller:
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --img-size 320
```

### 4. Pre-process Videos

```bash
# On a more powerful machine, convert videos before Jetson processing:
ffmpeg -i input.mp4 -vf "scale=640:480" -c:v h264 -crf 23 output_480p.mp4
```

### 5. Frame Skipping (if real-time not required)

```bash
# Process every 2nd or 3rd frame using ffmpeg
ffmpeg -i input.mp4 -vf "fps=10" output_10fps.mp4
```

## Troubleshooting

### Problem: Out of Memory (OOM) Error

**Solution**:
```bash
# Reduce input size
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --img-size 416

# Close other applications
killall firefox python3  # example

# Add swap space (see section above)

# Pre-process video to lower resolution
ffmpeg -i input.mp4 -vf "scale=640:480" output_480p.mp4
```

### Problem: Very Slow Processing

**Check**:
```bash
# 1. Monitor CPU/GPU temperature
vcgencmd measure_temp

# 2. Check if using CPU (slower) vs GPU
# In process_video_jetson.py output, look for "Device: cpu" or "Device: cuda"

# 3. Monitor memory pressure (causes swap slowdown)
free -h
```

**Solutions**:
- Use GPU if available: `--device cuda:0`
- Reduce input size: `--img-size 416`
- Close other applications
- Pre-resize videos to lower resolution

### Problem: Model Weights Not Found

```bash
# Check if weights file exists
ls -lh weights/End-to-end.pth

# Download from GitHub releases and verify
wget https://github.com/hustvl/YOLOP/releases/download/v0.0.1/End-to-end.pth
mv End-to-end.pth weights/
```

### Problem: CUDA Out of Memory

```bash
# Jetson Nano with GPU might have limited VRAM
# Use CPU instead:
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --device cpu

# Or reduce batch/model size
```

## Advanced Usage

### Custom Confidence/IOU Thresholds

```bash
# Stricter detection (fewer false positives):
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --conf-thres 0.5 \
    --iou-thres 0.5

# Lenient detection (more objects detected):
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --conf-thres 0.1 \
    --iou-thres 0.3
```

### Process with Logging

```bash
# Redirect output to log file
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    2>&1 | tee processing.log
```

### Batch Processing with Custom Settings

```bash
python3 batch_process_videos.py \
    --input-dir videos/input \
    --output-dir videos/output \
    --img-size 416 \
    --conf-thres 0.3 \
    --device cpu
```

## File Structure After Setup

```
YOLOP/
├── videos/
│   ├── input/              # Place input videos here
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── video3.mp4
│   └── output/             # Output videos saved here
│       ├── detected_video1.mp4
│       ├── detected_video2.mp4
│       └── detected_video3.mp4
├── weights/
│   └── End-to-end.pth      # Pre-trained model weights
├── lib/                    # YOLOP library code
├── tools/                  # Original training/testing scripts
├── process_video_jetson.py        # Single video processor (MAIN SCRIPT)
├── batch_process_videos.py        # Batch processor
├── setup_jetson_nano.sh           # Setup script
└── jetson_nano_config.cfg         # Configuration reference
```

## YOLOP Model Architecture Overview

### Three Task Branches:

1. **Detection Head** (YOLOv3-style):
   - Detects objects (vehicles, pedestrians, cyclists)
   - Output: Bounding boxes, class predictions, confidence scores

2. **Drivable Area Segmentation** (FCN-style):
   - Pixel-wise classification (drivable vs. non-drivable)
   - Output: Segmentation mask

3. **Lane Line Segmentation** (FCN-style):
   - Pixel-wise lane detection
   - Output: Lane segmentation mask

### Shared Encoder:
- Efficient backbone for feature extraction
- Shared between all three tasks to reduce computational cost

### Key Advantages:
- Real-time performance on embedded devices
- Joint training reduces redundant computation
- Multi-task learning improves generalization

## Model Inference Pipeline

```
Input Video
    ↓
Frame Extraction
    ↓
Resize/Preprocess (640x640 or custom size)
    ↓
YOLOP Model Inference
    ├── Detection Branch → Object boxes, confidence, class
    ├── DA Segmentation → Drivable area mask
    └── LL Segmentation → Lane detection mask
    ↓
Post-processing
    ├── Apply NMS to detection boxes
    ├── Interpolate segmentation masks back to original size
    └── Draw overlays on frame
    ↓
Output Frame
    ↓
Encode to Video
    ↓
Output: detected_{video_name}.mp4
```

## References

- **YOLOP GitHub**: https://github.com/hustvl/YOLOP
- **YOLOP Paper**: https://arxiv.org/abs/2108.11250
- **Jetson Nano Documentation**: https://docs.nvidia.com/jetson/jetson-nano/
- **PyTorch Documentation**: https://pytorch.org/docs/stable/

## License

YOLOP is released under the MIT License. See the original repository for details.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review YOLOP GitHub issues: https://github.com/hustvl/YOLOP/issues
3. Check Jetson Nano forums: https://forums.developer.nvidia.com/c/jetson/jetson-nano/

---

**Created for**: Jetson Nano 2GB deployment  
**YOLOP Version**: Based on latest main branch  
**Last Updated**: 2026  

