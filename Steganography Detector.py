#!/usr/bin/env python3
"""
Image Steganography Detector
Author: Danial Zivehdar
"""

from PIL import Image
import numpy as np
import os

class ImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
    
    def check_file_signature(self):
        """Check if file signature matches extension"""
        with open(self.image_path, 'rb') as f:
            header = f.read(16)
        
        signatures = {
            'jpg': [b'\xFF\xD8\xFF'],
            'png': [b'\x89PNG\r\n\x1a\n'],
            'gif': [b'GIF87a', b'GIF89a'],
            'bmp': [b'BM']
        }
        
        ext = self.image_path.split('.')[-1].lower()
        if ext in signatures:
            for sig in signatures[ext]:
                if header.startswith(sig):
                    return True, "Valid signature"
            return False, f"Invalid signature for .{ext}"
        return None, "Unknown extension"
    
    def check_embedded_files(self):
        """Check for embedded executables or scripts"""
        suspicious_markers = [
            b'MZ',           # Windows executable
            b'PK',           # ZIP archive
            b'\x7fELF',      # Linux executable
            b'#!/bin/bash',  # Bash script
            b'#!/usr/bin/python',  # Python script
            b'<script',      # HTML/JS
            b'eval(',        # Code execution
            b'exec(',        # Code execution
        ]
        
        with open(self.image_path, 'rb') as f:
            content = f.read()
        
        findings = []
        for marker in suspicious_markers:
            if marker in content:
                findings.append(marker.decode('utf-8', errors='ignore'))
        
        return findings
    
    def analyze_pixel_data(self):
        """Analyze LSB (Least Significant Bit) for steganography"""
        try:
            img_array = np.array(self.image)
            
            # Check LSB of red channel
            lsb = img_array[:, :, 0] & 1
            
            # Calculate entropy
            unique, counts = np.unique(lsb, return_counts=True)
            entropy = -np.sum((counts / counts.sum()) * np.log2(counts / counts.sum()))
            
            # High entropy in LSB suggests steganography
            return {
                'lsb_entropy': entropy,
                'suspicious': entropy > 0.95  # Threshold
            }
        except:
            return None
    
    def full_analysis(self):
        """Run complete analysis"""
        print(f"\n{'='*60}")
        print(f"IMAGE ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"File: {self.image_path}")
        print(f"Size: {os.path.getsize(self.image_path)} bytes")
        print(f"Dimensions: {self.image.size}")
        print(f"Mode: {self.image.mode}")
        
        # File signature check
        valid, msg = self.check_file_signature()
        print(f"\n[File Signature]")
        print(f"  Status: {'✓ Valid' if valid else '✗ Invalid'}")
        print(f"  Message: {msg}")
        
        # Embedded files check
        embedded = self.check_embedded_files()
        print(f"\n[Embedded Content]")
        if embedded:
            print(f"  ⚠️  SUSPICIOUS MARKERS FOUND:")
            for marker in embedded:
                print(f"    - {marker}")
        else:
            print(f"  ✓ No suspicious markers found")
        
        # Steganography check
        lsb_analysis = self.analyze_pixel_data()
        print(f"\n[Steganography Analysis]")
        if lsb_analysis:
            print(f"  LSB Entropy: {lsb_analysis['lsb_entropy']:.4f}")
            print(f"  Status: {'⚠️  HIGH - Possible steganography' if lsb_analysis['suspicious'] else '✓ Normal'}")
        else:
            print(f"  Could not analyze")
        
        print(f"\n{'='*60}")

# Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyzer = ImageAnalyzer(sys.argv[1])
        analyzer.full_analysis()
    else:
        print("Usage: python image_analyzer.py <image_path>")
