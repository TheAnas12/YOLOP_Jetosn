#!/bin/bash
# YOLOP Jetson Nano 2GB Setup Script
# This script sets up the environment for running YOLOP on Jetson Nano 2GB

echo "=========================================="
echo "YOLOP Setup for Jetson Nano 2GB"
echo "=========================================="

# Update system packages
echo "[1/7] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system dependencies
echo "[2/7] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1 \
    libjpeg-turbo-progs \
    libatlas-base-dev \
    libjasper-dev \
    libtiff-dev \
    libjpeg-dev \
    libharfbuzz0b \
    libwebp6 \
    python3-pip \
    git \
    wget

# Install PyTorch for Jetson Ara (ARM64)
echo "[3/7] Installing PyTorch for Jetson Nano ARM64..."
# For Jetson Nano, we use pre-built wheels
pip3 install --upgrade pip
pip3 install numpy

# Install PyTorch and TorchVision for ARM64
# These are pre-compiled for Jetson
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install YOLOP requirements
echo "[4/7] Installing YOLOP requirements..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --no-cache-dir
else
    echo "Warning: requirements.txt not found. Install manually."
fi

# Optional: Install TensorRT for optimization (if available)
echo "[5/7] Checking for TensorRT..."
if command -v trtexec &> /dev/null; then
    echo "TensorRT found. Consider using deploy/gen_wts.py for model acceleration."
else
    echo "TensorRT not found. Install from NVIDIA for better performance."
fi

# Create necessary directories
echo "[6/7] Creating directory structure..."
mkdir -p videos/input
mkdir -p videos/output
mkdir -p weights
mkdir -p logs

# Download pre-trained weights if not present
echo "[7/7] Checking for pre-trained weights..."
if [ ! -f "weights/End-to-end.pth" ]; then
    echo "Pre-trained weights not found."
    echo "Please download from: https://github.com/hustvl/YOLOP/releases"
    echo "And place in: weights/End-to-end.pth"
else
    echo "Pre-trained weights found!"
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Download pre-trained weights if not already done"
echo "2. Place your video files in: videos/input/"
echo "3. Run: python3 process_video_jetson.py --video videos/input/your_video.mp4"
echo ""
