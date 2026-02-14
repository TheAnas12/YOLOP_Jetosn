# Getting Started: YOLOP on Jetson Nano 2GB

## 60-Second Quick Start

```bash
# 1. Setup environment (run once)
chmod +x setup_jetson_nano.sh
./setup_jetson_nano.sh

# 2. Copy your video
cp your_video.mp4 videos/input/

# 3. Run interactive processor
python3 quick_process.py

# 4. Results in videos/output/detected_your_video.mp4
```

---

## Step-by-Step Setup

### Step 1: Clone/Setup YOLOP

This workflow assumes you have the YOLOP repository. If not:

```bash
git clone https://github.com/hustvl/YOLOP.git
cd YOLOP
```

### Step 2: Run Setup Script

On your Jetson Nano:

```bash
# Make script executable
chmod +x setup_jetson_nano.sh

# Run setup
./setup_jetson_nano.sh
```

This will:
- Update system packages
- Install Python dependencies
- Install PyTorch for ARM64
- Create necessary directories (`videos/`, `weights/`)

### Step 3: Download Model Weights

Download the pre-trained weights:

```bash
# Option 1: Manual download
# Visit: https://github.com/hustvl/YOLOP/releases
# Download End-to-end.pth
# Place in: weights/End-to-end.pth

# Option 2: Command line (if wget works)
cd weights
wget https://github.com/hustvl/YOLOP/releases/download/v0.0.1/End-to-end.pth
cd ..

# Verify
ls -lh weights/End-to-end.pth
```

### Step 4: Prepare Your Videos

```bash
# Create input directory (if not exists)
mkdir -p videos/input

# Copy your videos
cp video1.mp4 videos/input/
cp video2.mp4 videos/input/
cp video3.mp4 videos/input/

# Verify
ls -lh videos/input/
```

---

## Three Ways to Process Videos

### Method 1: Interactive Mode (Easiest)

```bash
python3 quick_process.py
```

This will:
1. Show available videos in `videos/input/`
2. Let you select which videos to process
3. Ask you to choose device (CPU/GPU) and mode (fast/balanced)
4. Process automatically
5. Show results location

**Best for**: First time use, casual processing

### Method 2: Single Video (Command Line)

```bash
python3 quick_process.py -v videos/input/my_video.mp4
```

Options:
```bash
--fast    # Use faster inference (lower accuracy)
--gpu     # Use GPU instead of CPU
```

Examples:
```bash
# Standard processing
python3 quick_process.py -v videos/input/test.mp4

# Fast mode for Jetson Nano 2GB
python3 quick_process.py -v videos/input/test.mp4 --fast

# Using GPU (if available)
python3 quick_process.py -v videos/input/test.mp4 --gpu
```

**Best for**: Scripting, integration

### Method 3: Advanced Processing

```bash
python3 process_video_jetson.py \
    --video videos/input/my_video.mp4 \
    --weights weights/End-to-end.pth \
    --output-dir videos/output \
    --img-size 640 \
    --conf-thres 0.25 \
    --iou-thres 0.45 \
    --device cpu
```

Full options:
```
--video           : Input video path (required)
--weights         : Model weights (default: weights/End-to-end.pth)
--output-dir      : Output directory (default: videos/output)
--img-size        : Input resolution (default: 640)
--conf-thres      : Detection confidence (0.0-1.0, default: 0.25)
--iou-thres       : NMS threshold (0.0-1.0, default: 0.45)
--device          : cuda:0 or cpu (default: cpu)
--half            : Use FP16 precision (if CUDA >= 7.0)
```

**Best for**: Fine-tuning parameters, optimization

### Method 4: Batch Processing

Process all videos at once:

```bash
python3 batch_process_videos.py \
    --input-dir videos/input \
    --output-dir videos/output
```

Options: same as `process_video_jetson.py`

**Best for**: Processing multiple videos

---

## Output Files

### Location

All processed videos are saved in `videos/output/`

### Naming Convention

| Input | Output |
|-------|--------|
| `video1.mp4` | `detected_video1.mp4` |
| `street_scene.mp4` | `detected_street_scene.mp4` |
| `highway.mp4` | `detected_highway.mp4` |

### What's in the Output

The output videos show:

1. **Green overlay** - Drivable road area
2. **Yellow lines** - Detected lane markings
3. **Red/colored boxes** - Detected objects (vehicles, pedestrians, etc.)
4. **Labels** - Object class and confidence score

Each detection box shows:
- Class name (e.g., "car", "person", "bicycle")
- Confidence (0-1.0, e.g., 0.92 = 92% confident)

---

## Real-Time Processing Performance

### Expected Speed on Jetson Nano 2GB

| Video Resolution | Processing Speed | Memory | Quality |
|------------------|------------------|--------|---------|
| **480p** | 100-150 ms/frame | 600 MB | Good |
| **720p** | 200-300 ms/frame | 800 MB | Excellent |
| **1080p** | 400-600 ms/frame | 1000+MB | Best (may swap) |

### Recommended Settings

For **real-time-ish** performance on Jetson Nano 2GB:

```bash
# Best balance of speed and accuracy
python3 quick_process.py -v videos/input/video.mp4 --fast

# Or detailed command:
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --img-size 416 \
    --device cpu
```

---

## Troubleshooting

### "Model weights not found"

```bash
# Check if weights exist
ls -lh weights/End-to-end.pth

# If missing, download from:
# https://github.com/hustvl/YOLOP/releases
# Then place in weights/ directory
```

### "Out of Memory" Error

**Fix options**:

```bash
# 1. Use fast mode (lower resolution)
python3 quick_process.py -v videos/input/video.mp4 --fast

# 2. Pre-resize video on a more powerful machine
ffmpeg -i large_video.mp4 -vf "scale=640:480" video_small.mp4 videos/input/

# 3. Add swap space to Jetson Nano
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Very Slow Processing

**Check temperature**:
```bash
vcgencmd measure_temp
```

If hot (>60°C), your Jetson may be throttling. Solution:
- Let it cool down
- Increase air flow
- Use heatsink/fan

**Check device being used**:
```bash
# Should show "Device: cpu" or "Device: cuda" at start
python3 quick_process.py -v videos/input/video.mp4
```

### Script Not Working

1. **Check Python version**:
   ```bash
   python3 --version  # Should be 3.7+
   ```

2. **Check directory structure**:
   ```bash
   ls -la  # Should show lib/, tools/, weights/, videos/
   ```

3. **Check YOLOP installation**:
   ```bash
   python3 -c "from lib.models import get_net; print('✓ YOLOP OK')"
   ```

4. **Check PyTorch**:
   ```bash
   python3 -c "import torch; print(f'✓ PyTorch {torch.__version__}')"
   ```

---

## Tips for Success

### 1. Monitor System Resources

```bash
# Before running (watch memory and CPU)
watch -n 1 'free -h; echo "---"; top -b -n 1 | head -n 5'
```

### 2. Process During Off-Peak

- Process videos when not running other applications
- Close browser, GUI heavy apps
- Jetson Nano has limited resources

### 3. Prepare Videos Beforehand

On a more powerful machine:
```bash
# Convert 1080p to 720p
ffmpeg -i input_1080p.mp4 -vf "scale=1280:720" -c:v h264 -crf 23 output_720p.mp4

# This will be much faster on Jetson Nano
```

### 4. Adjust Parameters for Your Needs

```bash
# More detections (lower confidence):
--conf-thres 0.1

# Fewer detections (higher confidence):
--conf-thres 0.5

# Faster inference:
--img-size 416

# Higher accuracy:
--img-size 960
```

---

## Understanding Output Quality

### Detection Confidence Scores

- **0.90-1.00**: Very confident (good detection)
- **0.70-0.90**: Confident (usually correct)
- **0.50-0.70**: Less confident (may miss some details)
- **< 0.50**: Low confidence (often false positives)

Default threshold: **0.25** (catches most objects)

To only see high-confidence detections:
```bash
python3 process_video_jetson.py \
    --video videos/input/video.mp4 \
    --conf-thres 0.5
```

### Area Definitions

- **Green (Drivable Area)**: Where vehicle can safely drive
- **Non-green**: Non-drivable areas (sidewalk, off-road, etc.)
- **Yellow (Lane Lines)**: Detected lane markings
- **Boxes**: Individual object detections

---

## Next Steps

1. **Explore Parameters**: Try different `--conf-thres` and `--img-size` values
2. **Optimize for Your Use Case**: Fast vs. Accurate
3. **Process Batch**: Use `batch_process_videos.py` for multiple videos
4. **Deploy**: Use output videos in your application

---

## More Information

For detailed information:
- Read: [JETSON_NANO_WORKFLOW.md](JETSON_NANO_WORKFLOW.md)
- Config: [jetson_nano_config.cfg](jetson_nano_config.cfg)
- YOLOP GitHub: https://github.com/hustvl/YOLOP

---

## Quick Reference

```bash
# Setup (one time)
chmod +x setup_jetson_nano.sh && ./setup_jetson_nano.sh

# Prepare videos
mkdir -p videos/input && cp your_video.mp4 videos/input/

# Process (interactive)
python3 quick_process.py

# Process (single video)
python3 quick_process.py -v videos/input/video.mp4

# Process (fast mode)
python3 quick_process.py -v videos/input/video.mp4 --fast

# Process (batch)
python3 batch_process_videos.py --input-dir videos/input

# Find results
ls -lh videos/output/
```

---

Good luck! 🚀

