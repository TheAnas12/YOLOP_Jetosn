#!/usr/bin/env python3
"""
YOLOP Video Processing for Jetson Nano 2GB
Processesunts videos frame by frame with YOLOP inference
Input:  {video_name}.mp4
Output: detected_{video_name}.mp4
"""

import argparse
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn
import torchvision.transforms as transforms
from tqdm import tqdm

# Add parent directory to path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from lib.config import cfg
from lib.config import update_config
from lib.core.function import AverageMeter
from lib.core.general import non_max_suppression, scale_coords
from lib.core.postprocess import morphological_process, connect_lane
from lib.dataset import LoadImages, LoadStreams
from lib.models import get_net
from lib.utils import plot_one_box, show_seg_result
from lib.utils.utils import (create_logger, select_device, time_synchronized)


class JetsonNanoOptimizer:
    """Optimization techniques for Jetson Nano 2GB"""
    
    @staticmethod
    def reduce_memory_footprint():
        """Configure PyTorch for minimal memory usage"""
        torch.cuda.empty_cache()
        cudnn.benchmark = False
        cudnn.enabled = True
        
    @staticmethod
    def enable_half_precision():
        """Enable half (FP16) precision for faster inference"""
        return torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 7
        

def load_model(weights_path, device, is_half):
    """Load YOLOP model with optimizations for Jetson Nano"""
    model = get_net(cfg)
    
    if weights_path and os.path.exists(weights_path):
        state_dict = torch.load(weights_path, map_location=device)
        if 'state_dict' in state_dict:
            model.load_state_dict(state_dict['state_dict'])
        else:
            model.load_state_dict(state_dict)
        print(f"✓ Loaded weights from: {weights_path}")
    else:
        print(f"✗ Weights not found: {weights_path}")
        sys.exit(1)
    
    model = model.to(device)
    if is_half:
        model = model.half()
    model.eval()
    
    return model


def process_video(model, video_path, output_path, device, is_half, opt):
    """Process video file with YOLOP"""
    
    # Open video
    vid_cap = cv2.VideoCapture(str(video_path))
    if not vid_cap.isOpened():
        print(f"✗ Failed to open video: {video_path}")
        return False
    
    # Get video properties
    fps = int(vid_cap.get(cv2.CAP_PROP_FPS))
    width = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\n{'='*60}")
    print(f"Video: {Path(video_path).name}")
    print(f"Resolution: {width}x{height} @ {fps} FPS")
    print(f"Total frames: {total_frames}")
    print(f"Output: {Path(output_path).name}")
    print(f"{'='*60}\n")
    
    # Video writer setup
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vid_writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    if not vid_writer.isOpened():
        print(f"✗ Failed to open video writer: {output_path}")
        vid_cap.release()
        return False
    
    # Get model names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[np.random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]
    
    # Initialize timing
    inf_time = AverageMeter()
    nms_time = AverageMeter()
    
    # Warm-up inference
    with torch.no_grad():
        dummy_img = torch.zeros((1, 3, opt.img_size, opt.img_size), device=device)
        if is_half:
            dummy_img = dummy_img.half()
        _ = model(dummy_img)
    
    # Prepare transform
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    transform = transforms.Compose([
        transforms.ToTensor(),
        normalize,
    ])
    
    frame_count = 0
    
    # Process frames
    with torch.no_grad():
        with tqdm(total=total_frames, desc="Processing", unit="frame") as pbar:
            while True:
                ret, frame = vid_cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Resize frame for model input
                img_det = cv2.resize(frame, (opt.img_size, opt.img_size))
                img_tensor = transform(img_det).to(device)
                
                if is_half:
                    img_tensor = img_tensor.half()
                else:
                    img_tensor = img_tensor.float()
                
                if img_tensor.ndimension() == 3:
                    img_tensor = img_tensor.unsqueeze(0)
                
                # Inference
                t1 = time_synchronized()
                det_out, da_seg_out, ll_seg_out = model(img_tensor)
                t2 = time_synchronized()
                inf_time.update(t2 - t1, img_tensor.size(0))
                
                # Apply NMS
                t3 = time_synchronized()
                inf_out, _ = det_out
                det_pred = non_max_suppression(
                    inf_out,
                    conf_thres=opt.conf_thres,
                    iou_thres=opt.iou_thres,
                    classes=None,
                    agnostic=False
                )
                t4 = time_synchronized()
                nms_time.update(t4 - t3, img_tensor.size(0))
                
                det = det_pred[0]
                
                # Process segmentation outputs
                _, _, h_model, w_model = img_tensor.shape
                
                # Drivable area segmentation
                da_predict = da_seg_out[:, :, :, :]
                da_seg_mask = torch.nn.functional.interpolate(
                    da_predict,
                    size=(height, width),
                    mode='bilinear'
                )
                _, da_seg_mask = torch.max(da_seg_mask, 1)
                da_seg_mask = da_seg_mask.int().squeeze().cpu().numpy()
                
                # Lane line segmentation
                ll_predict = ll_seg_out[:, :, :, :]
                ll_seg_mask = torch.nn.functional.interpolate(
                    ll_predict,
                    size=(height, width),
                    mode='bilinear'
                )
                _, ll_seg_mask = torch.max(ll_seg_mask, 1)
                ll_seg_mask = ll_seg_mask.int().squeeze().cpu().numpy()
                
                # Draw segmentation
                frame = show_seg_result(
                    frame,
                    (da_seg_mask, ll_seg_mask),
                    None,
                    None,
                    is_demo=True
                )
                
                # Scale detection boxes and draw
                if len(det):
                    det[:, :4] = scale_coords(
                        img_tensor.shape[2:],
                        det[:, :4],
                        frame.shape
                    ).round()
                    
                    for *xyxy, conf, cls in reversed(det):
                        label_det_pred = f'{names[int(cls)]} {conf:.2f}'
                        plot_one_box(
                            xyxy,
                            frame,
                            label=label_det_pred,
                            color=colors[int(cls)],
                            line_thickness=2
                        )
                
                # Write frame
                vid_writer.write(frame)
                
                # Update progress
                pbar.update(1)
                pbar.set_postfix({
                    "Inf": f"{inf_time.avg:.3f}s",
                    "NMS": f"{nms_time.avg:.3f}s"
                })
    
    # Cleanup
    vid_cap.release()
    vid_writer.release()
    
    total_time = inf_time.avg * total_frames + nms_time.avg * total_frames
    print(f"\n✓ Processing complete!")
    print(f"  Inference time: {inf_time.avg:.4f}s/frame")
    print(f"  NMS time: {nms_time.avg:.4f}s/frame")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Output saved to: {output_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='YOLOP Video Processing for Jetson Nano 2GB'
    )
    parser.add_argument(
        '--video',
        type=str,
        required=True,
        help='Input video path (e.g., videos/input/test.mp4)'
    )
    parser.add_argument(
        '--weights',
        type=str,
        default='weights/End-to-end.pth',
        help='Path to model weights'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='videos/output',
        help='Output directory for processed videos'
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
    
    # Validate input
    if not os.path.exists(args.video):
        print(f"✗ Video file not found: {args.video}")
        sys.exit(1)
    
    # Setup
    JetsonNanoOptimizer.reduce_memory_footprint()
    
    device = select_device(args.device)
    is_half = args.half and JetsonNanoOptimizer.enable_half_precision()
    
    print(f"\nDevice: {device}")
    print(f"Half precision (FP16): {is_half}")
    print()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate output filename
    video_name = Path(args.video).stem
    output_filename = f"detected_{video_name}.mp4"
    output_path = os.path.join(args.output_dir, output_filename)
    
    # Load model
    print("Loading model...")
    model = load_model(args.weights, device, is_half)
    
    # Process video
    try:
        success = process_video(model, args.video, output_path, device, is_half, args)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
