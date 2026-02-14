# YOLOP Jetson Nano 2GB Workflow - File Index

## 📋 Overview

This document lists all files created for the YOLOP workflow. Each file has a specific purpose in the workflow.

---

## 🚀 Main Processing Scripts (What You Use)

### 1. **quick_process.py** ⭐ RECOMMENDED FOR FIRST TIME

**Purpose**: Interactive video processor - easiest to use  
**When to use**: First-time users, casual processing  
**How to run on Jetson**:
```bash
python3 quick_process.py
```

**Features**:
- Shows available videos
- Interactive selection
- Automatic device/mode choice
- Progress indicators
- Error handling

**Output**: `detected_{video_name}.mp4`

---

### 2. **process_video_jetson.py** ⭐ MAIN SCRIPT

**Purpose**: Process single video with full control  
**When to use**: Want to specify exact parameters  
**How to run on Jetson**:
```bash
python3 process_video_jetson.py --video videos/input/my_video.mp4
```

**Key features**:
- Full parameter control
- Memory optimizations for 2GB RAM
- Detailed timing info
- Professional-grade processing

**Parameters**:
- `--video`: Input video path
- `--img-size`: Input resolution (default: 640)
- `--conf-thres`: Detection confidence (default: 0.25)
- `--iou-thres`: NMS threshold (default: 0.45)
- `--device`: cpu or cuda:0
- `--half`: Use FP16 precision

**Example**:
```bash
python3 process_video_jetson.py \
    --video videos/input/test.mp4 \
    --img-size 416 \
    --conf-thres 0.3
```

---

### 3. **batch_process_videos.py**

**Purpose**: Process all videos in directory automatically  
**When to use**: Multiple videos to process  
**How to run on Jetson**:
```bash
python3 batch_process_videos.py --input-dir videos/input
```

**Features**:
- Processes all .mp4 files
- Auto-detects already processed videos
- Same parameters as process_video_jetson.py
- Summary statistics

**Example**: Process all videos with fast settings
```bash
python3 batch_process_videos.py \
    --input-dir videos/input \
    --img-size 416
```

---

## 🛠️ Setup & Configuration (Run Once)

### 4. **setup_jetson_nano.sh**

**Purpose**: One-time environment setup on Jetson Nano  
**When to run**: First time on Jetson Nano  
**How to run on Jetson**:
```bash
chmod +x setup_jetson_nano.sh
./setup_jetson_nano.sh
```

**What it does**:
- Updates system packages
- Installs Python dependencies
- Installs PyTorch for ARM64
- Installs YOLOP requirements
- Creates directories (`videos/`, `weights/`)
- Verifies TensorRT (if available)

**Takes**: ~10-20 minutes depending on internet

---

### 5. **jetson_nano_config.cfg**

**Purpose**: Reference configuration file with optimization tips  
**When to use**: Check recommended settings  
**How to use**:
- Open with text editor
- Read optimization recommendations
- Reference section headings for specific issues

**Contents**:
- System configuration
- Memory optimization settings
- Model inference parameters
- Performance expectations
- Troubleshooting guide

**Not programmatic** - Just a reference document

---

## 📖 Documentation (Read These!)

### 6. **QUICKSTART.md** ⭐ START HERE

**Purpose**: 60-second quick start guide  
**When to read**: Before doing anything else  
**Contents**:
- Quick setup (3 steps)
- Step-by-step walkthrough
- Three ways to process videos
- Performance expectations
- Troubleshooting
- Tips for success

**Reading time**: 5-10 minutes

**On Jetson, view with**:
```bash
cat QUICKSTART.md
less QUICKSTART.md  # or
```

---

### 7. **JETSON_NANO_WORKFLOW.md** ⭐ COMPREHENSIVE GUIDE

**Purpose**: Complete reference documentation  
**When to read**: Need detailed information, optimization tips  
**Contents**:
- What is YOLOP? (detailed explanation)
- Full quick start
- Command line arguments
- Output format explanation
- Performance characteristics
- Memory optimization
- Troubleshooting with solutions
- Advanced usage
- Model architecture explanation
- YOLOP inference pipeline

**Reading time**: 20-30 minutes (reference style)

**On Jetson, view with**:
```bash
cat JETSON_NANO_WORKFLOW.md
less JETSON_NANO_WORKFLOW.md
```

---

### 8. **README_SUMMARY.txt** (This is reference)

**Purpose**: High-level overview of entire workflow  
**When to read**: Get oriented, understand what was created  
**Contents**:
- Files overview
- How YOLOP works
- Quick start
- Three ways to use
- File structure
- Setup checklist
- Troubleshooting quick ref
- Next steps

**Reading time**: 10 minutes

**On Jetson, view with**:
```bash
cat README_SUMMARY.txt
```

---

## 🖥️ Windows Helper (For Preparation)

### 9. **workflow_helper.bat**

**Purpose**: Windows batch script for workflow preparation  
**When to use**: On your Windows machine (not on Jetson)  
**How to run**:
```bash
workflow_helper.bat
```

**Menu options**:
1. Create directory structure
2. Check workflow files
3. Show video instructions
4. Show documentation
5. Exit

**Features**:
- Creates `videos/input/`, `videos/output/`, `weights/`
- Verifies all necessary files exist
- Shows video preparation instructions
- Points to documentation

**Note**: This is just a helper. Real processing happens on Jetson Nano.

---

## 📁 Directory Structure After Using Files

After setup, your YOLOP directory will look like:

```
YOLOP/
│
├── 🎬 PROCESSING SCRIPTS (Run these on Jetson)
│   ├── quick_process.py              ⭐ Best for beginners
│   ├── process_video_jetson.py       ⭐ For full control
│   └── batch_process_videos.py       For multiple videos
│
├── 🔧 SETUP & CONFIG (Run/read once)
│   ├── setup_jetson_nano.sh          ⭐ Run on Jetson first time
│   └── jetson_nano_config.cfg        Reference config
│
├── 📚 DOCUMENTATION (Read on any machine)
│   ├── QUICKSTART.md                 ⭐ Start here!
│   ├── JETSON_NANO_WORKFLOW.md       ⭐ Complete guide
│   └── README_SUMMARY.txt            Overview
│
├── 🖥️ WINDOWS HELPER (Use on Windows)
│   └── workflow_helper.bat           For prep
│
├── 🎥 VIDEO DIRECTORIES (Created by setup/helper)
│   ├── videos/
│   │   ├── input/                    (Place your .mp4 here)
│   │   └── output/                   (Output goes here)
│   └── weights/
│       └── End-to-end.pth            (Download model weights)
│
├── lib/                              (From YOLOP repo)
├── tools/                            (From YOLOP repo)
└── ... (other YOLOP files)
```

---

## 🎯 Quick Reference: Which File To Use When

### "I just got Jetson Nano, what do I do?"
→ Read **QUICKSTART.md**

### "I want to understand YOLOP"
→ Read **JETSON_NANO_WORKFLOW.md**

### "I'm on my Jetson Nano and ready to process"
1. Run `./setup_jetson_nano.sh` (one time)
2. Copy videos to `videos/input/`
3. Run `python3 quick_process.py`

### "I want to process one video with specific settings"
→ Use `python3 process_video_jetson.py` with parameters

### "I have multiple videos"
→ Use `python3 batch_process_videos.py`

### "I'm on Windows and preparing"
1. Run `workflow_helper.bat` to create directories
2. Copy videos to `videos/input/`
3. Transfer entire YOLOP folder to Jetson

### "Something went wrong"
→ Check troubleshooting in:
- **QUICKSTART.md** - Common issues
- **JETSON_NANO_WORKFLOW.md** - Detailed solutions

---

## 📋 Setup Checklist

- [ ] Read QUICKSTART.md (5 min)
- [ ] Transfer YOLOP folder to Jetson Nano
- [ ] Run `./setup_jetson_nano.sh` on Jetson (15-20 min)
- [ ] Download model weights: `weights/End-to-end.pth` (from GitHub)
- [ ] Create `videos/input/` and add your .mp4 files
- [ ] Run `python3 quick_process.py` on Jetson
- [ ] Check output in `videos/output/detected_*.mp4`

---

## 🔄 Typical Workflow

### On Windows (Preparation)
```
1. Run workflow_helper.bat
2. Prepare videos (convert, resize if needed)
3. Copy to videos/input/
```

### On Jetson Nano (Processing)
```
1. Transfer YOLOP folder
2. Run ./setup_jetson_nano.sh
3. Download weights
4. Run python3 quick_process.py
5. Check videos/output/ for results
6. Transfer results back to Windows
```

---

## 📊 File Usage Statistics

| File | Type | Critical | Platform | Run/Read |
|------|------|----------|----------|----------|
| quick_process.py | Script | ⭐⭐⭐ | Jetson | Run |
| process_video_jetson.py | Script | ⭐⭐⭐ | Jetson | Run |
| batch_process_videos.py | Script | ⭐⭐ | Jetson | Run |
| setup_jetson_nano.sh | Script | ⭐⭐⭐ | Jetson | Run (once) |
| QUICKSTART.md | Doc | ⭐⭐⭐ | Any | Read |
| JETSON_NANO_WORKFLOW.md | Doc | ⭐⭐⭐ | Any | Read |
| jetson_nano_config.cfg | Config | ⭐ | Any | Reference |
| workflow_helper.bat | Script | ⭐ | Windows | Run |
| README_SUMMARY.txt | Doc | ⭐⭐ | Any | Read |

---

## 🆘 Help Navigation

### "How do I...?"

**...set up Jetson Nano?**
→ QUICKSTART.md → "Step-by-Step Setup"

**...process a single video?**
→ QUICKSTART.md → "Three Ways to Process Videos" → Method 1 or 2

**...process multiple videos?**
→ QUICKSTART.md → "Three Ways" → Method 4, or use batch_process_videos.py

**...fix out of memory errors?**
→ JETSON_NANO_WORKFLOW.md → "Troubleshooting"

**...understand the output?**
→ JETSON_NANO_WORKFLOW.md → "Output Format and Visualization"

**...optimize for speed?**
→ JETSON_NANO_WORKFLOW.md → "Performance on Jetson Nano 2GB"

**...use advanced parameters?**
→ JETSON_NANO_WORKFLOW.md → "Command Line Arguments"

---

## 📞 Support

For each type of issue, check these files in order:

1. **Setup issues**: QUICKSTART.md Troubleshooting
2. **Processing issues**: JETSON_NANO_WORKFLOW.md Troubleshooting
3. **Performance issues**: jetson_nano_config.cfg optimization tips
4. **General questions**: README_SUMMARY.txt overview

---

## Version Information

- **YOLOP Version**: Latest from main branch
- **Python**: 3.7+
- **Platform**: Jetson Nano 2GB with JetPack
- **Created**: 2026
- **Documentation**: Complete and up-to-date

---

## Notes

- All Python scripts are designed for Jetson Nano 2GB specifically
- Memory optimizations are built-in
- File naming convention: Input `{name}.mp4` → Output `detected_{name}.mp4`
- All processing happens on Jetson (not remote)
- Weights must be downloaded separately from GitHub

---

**Ready to get started?**

1. Transfer files to Jetson Nano
2. Read QUICKSTART.md
3. Run setup script
4. Process your first video!

Good luck! 🚀

