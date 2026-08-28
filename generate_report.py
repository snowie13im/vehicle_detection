#!/usr/bin/env python3
"""Generate a summary report of detection results."""

import re
import sys
from pathlib import Path
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def parse_detections(output_text):
    """Parse detection results from script output."""
    results = {
        'images': [],
        'videos': [],
        'total_detections': {},
        'processing_time': 0
    }
    
    # Find all image lines
    image_pattern = r'image \d+/\d+ .+?\.(jpeg|jpg|png): (.+?) Done\. \(([0-9.]+)s\)'
    for match in re.finditer(image_pattern, output_text):
        filename = match.group(0).split('/')[-1].split(':')[0]
        detections = match.group(2)
        time = float(match.group(3))
        results['images'].append({
            'file': filename,
            'detections': detections,
            'time': time
        })
    
    # Find all video lines
    video_pattern = r'video \d+/\d+ .+?\.(mp4|avi):'
    current_video = None
    for line in output_text.split('\n'):
        if 'video' in line and '.mp4' in line or '.avi' in line:
            parts = line.split('/')
            if len(parts) > 1:
                filename = parts[-1].split(':')[0].strip()
                if filename and filename not in [v['file'] for v in results['videos']]:
                    current_video = {'file': filename, 'frames': 0}
                    results['videos'].append(current_video)
        elif current_video and 'Done.' in line:
            current_video['frames'] += 1
    
    return results

def generate_report(log_file=None):
    """Generate a detection report."""
    
    # Read recent output
    if log_file and Path(log_file).exists():
        with open(log_file, 'r') as f:
            output_text = f.read()
    else:
        print(f"{RED}Log file not found. Running detection first...{RESET}\n")
        return
    
    results = parse_detections(output_text)
    
    # Generate report
    report = f"""
{BOLD}{'='*70}
  VEHICLE DETECTION REPORT
{BOLD}{'='*70}{RESET}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: YOLOv5 (runs/train/exp12/weights/best.pt)
Confidence Threshold: 0.25

{BOLD}SUMMARY{RESET}
{'-'*70}
Total Images Processed: {len(results['images'])}
Total Videos Processed: {len(results['videos'])}

{BOLD}IMAGE DETECTION RESULTS{RESET}
{'-'*70}
"""
    
    total_cars = 0
    total_bikes = 0
    total_trucks = 0
    total_buses = 0
    total_bicycles = 0
    
    for img in results['images']:
        detections = img['detections']
        report += f"\n📷 {img['file']}\n"
        report += f"   Detections: {detections}\n"
        report += f"   Processing Time: {img['time']:.3f}s\n"
        
        # Count vehicles
        if 'Car' in detections:
            cars = int(re.search(r'(\d+)\s+Car', detections).group(1))
            total_cars += cars
        if 'Motorcycle' in detections or 'Motorcycle' in detections:
            motorcycles = int(re.search(r'(\d+)\s+Motorcycle', detections).group(1)) if re.search(r'(\d+)\s+Motorcycle', detections) else 0
            total_bikes += motorcycles
        if 'Truck' in detections:
            trucks = int(re.search(r'(\d+)\s+Truck', detections).group(1))
            total_trucks += trucks
        if 'Bus' in detections:
            buses = int(re.search(r'(\d+)\s+Bus', detections).group(1))
            total_buses += buses
        if 'Bicycle' in detections:
            bicycles = int(re.search(r'(\d+)\s+Bicycle', detections).group(1))
            total_bicycles += bicycles
    
    if results['videos']:
        report += f"\n{BOLD}VIDEO DETECTION RESULTS{RESET}\n{'-'*70}\n"
        for vid in results['videos']:
            report += f"\n🎬 {vid['file']}\n"
            report += f"   Frames Processed: {vid['frames']}\n"
    
    report += f"\n{BOLD}TOTAL VEHICLE COUNTS{RESET}\n{'-'*70}\n"
    report += f"{GREEN}🚗 Cars:{RESET} {total_cars}\n"
    report += f"{YELLOW}🏍️ Motorcycles:{RESET} {total_bikes}\n"
    report += f"{RED}🚚 Trucks:{RESET} {total_trucks}\n"
    report += f"{BLUE}🚌 Buses:{RESET} {total_buses}\n"
    report += f"🚲 Bicycles: {total_bicycles}\n"
    
    total_vehicles = total_cars + total_bikes + total_trucks + total_buses + total_bicycles
    report += f"\n{BOLD}Total Vehicles Detected:{RESET} {total_vehicles}\n"
    
    report += f"\n{'='*70}\n"
    report += f"Results saved to: runs/detect/full_report\n"
    report += f"Annotated images available in results folder.\n"
    report += f"{'='*70}\n"
    
    return report

if __name__ == '__main__':
    print(f"\n{BOLD}{YELLOW}Parsing detection results...{RESET}\n")
    # For now, just create a template - we'll run detection first
    print("Please wait for detection to complete, then run: python generate_report.py")
