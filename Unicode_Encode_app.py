#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import logging
import subprocess
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template_string

# ─────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==========================================
# 1. Core Logic (From your original script)
# ==========================================
def get_storage_paths():
    base_storages = []
    storage_root = "/storage"
    if os.path.exists(storage_root):
        for path in os.listdir(storage_root):
            full_path = os.path.join(storage_root, path)
            if os.path.isdir(full_path) and os.access(full_path, os.R_OK):
                if path in ['emulated', 'self'] or '-' in path:
                    if path == 'emulated':
                        final_path = os.path.join(full_path, '0')
                        if os.path.exists(final_path):
                            base_storages.append(final_path)
                    else:
                        base_storages.append(full_path)
    if not base_storages:
        base_storages.append("/storage/emulated/0")
    return base_storages

STORAGE_PATHS = get_storage_paths()
RELATIVE_SOURCE_DIRS = [
    "Android/data/org.telegram.messenger", "Android/data/com.whatsapp",
    "Android/data/com.google.android.youtube", "Download", "Documents",
    "Pictures", "DCIM", "Music", "Movies",
]
TARGET_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', 
    '.jpg', '.jpeg', '.png', '.zip', '.rar',
    '.mp4', '.mkv', '.avi', '.mp3', '.wav', '.flac', '.m4a'
}
SPECIFIC_FILES = ["finance.xls", "important_data.db"]
LOCAL_DEST_DIR = os.path.join("/storage/emulated/0", "resultfilesuploaded")
BATCH_SIZE = 20
MEDIA_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mp3', '.wav', '.flac', '.m4a', '.jpg', '.jpeg', '.png'}

def format_size(size_in_bytes):
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

def flush_storage_cache():
    try:
        os.sync()
        subprocess.run(['sync'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.debug(f"Sync warning: {e}")

def safe_move_file(src: str, dst: str) -> bool:
    try:
        shutil.move(src, dst)
        return True
    except OSError:
        try:
            shutil.copy2(src, dst)
            time.sleep(0.05)
            os.remove(src)
            return True
        except Exception as e:
            logger.error(f"Error in safe move for {src}: {e}")
            return False

def scan_files():
    found_files = []
    for storage in STORAGE_PATHS:
        for rel_dir in RELATIVE_SOURCE_DIRS:
            target_dir = os.path.join(storage, rel_dir)
            if not os.path.exists(target_dir) or not os.access(target_dir, os.R_OK):
                continue
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    if ext in TARGET_EXTENSIONS or file.lower() in [f.lower() for f in SPECIFIC_FILES]:
                        try:
                            size = os.path.getsize(file_path)
                            found_files.append({"path": file_path, "size": size, "ext": ext, "name": file})
                        except OSError:
                            continue
    return found_files

def organize_and_clean_files(files):
    if not files:
        return {"moved": 0, "failed": 0}
    
    os.makedirs(LOCAL_DEST_DIR, exist_ok=True)
    moved_count = 0
    failed_count = 0
    
    for i, file_info in enumerate(files):
        file_path = file_info['path']
        ext = file_info['ext']
        try:
            filename = file_info['name']
            dest_path = os.path.join(LOCAL_DEST_DIR, filename)
            counter = 1
            while os.path.exists(dest_path):
                name, _ = os.path.splitext(filename)
                dest_path = os.path.join(LOCAL_DEST_DIR, f"{name}_{counter}{ext}")
                counter += 1
                
            if safe_move_file(file_path, dest_path):
                moved_count += 1
            else:
                failed_count += 1
                
            if (i + 1) % BATCH_SIZE == 0 or ext in MEDIA_EXTENSIONS:
                flush_storage_cache()
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")
            failed_count += 1
            
    flush_storage_cache()
    return {"moved": moved_count, "failed": failed_count}

# ==========================================
# 2. Web API Endpoints
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Storage Manager</title>
    <style>
        :root { --bg: #121212; --surface: #1e1e1e; --primary: #007acc; --text: #e0e0e0; --success: #4caf50; --warning: #ff9800; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: var(--primary); }
        .card { background: var(--surface); padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .btn { background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; transition: 0.3s; }
        .btn:disabled { background: #555; cursor: not-allowed; }
        .btn:hover:not(:disabled) { background: #005fa3; }
        .log-box { background: #000; color: #0f0; font-family: monospace; padding: 15px; border-radius: 4px; height: 200px; overflow-y: auto; font-size: 13px; }
        .file-list { max-height: 300px; overflow-y: auto; }
        .file-item { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #333; font-size: 14px; }
        .file-item:last-child { border-bottom: none; }
        .status { text-align: center; margin-top: 10px; font-weight: bold; }
        .spinner { display: none; border: 4px solid #333; border-top: 4px solid var(--primary); border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 10px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Smart Storage Manager</h1>
        
        <div class="card">
            <h3>1. Scan Storage</h3>
            <p>Scans Internal & SD Card for target files (Documents, Media, etc.)</p>
            <button class="btn" id="scanBtn" onclick="startScan()">Start Scanning</button>
            <div class="spinner" id="scanSpinner"></div>
            <div class="status" id="scanStatus"></div>
        </div>

        <div class="card" id="resultsCard" style="display:none;">
            <h3>2. Review Found Files (<span id="fileCount">0</span>)</h3>
            <div class="file-list" id="fileList"></div>
            <button class="btn" id="moveBtn" onclick="startMove()" style="background: var(--success);">Move & Clean Files</button>
            <div class="spinner" id="moveSpinner"></div>
            <div class="status" id="moveStatus"></div>
        </div>

        <div class="card">
            <h3>System Logs</h3>
            <div class="log-box" id="logBox"></div>
        </div>
    </div>

    <script>
        function addLog(message) {
            const logBox = document.getElementById('logBox');
            const time = new Date().toLocaleTimeString();
            logBox.innerHTML += `[${time}] ${message}<br>`;
            logBox.scrollTop = logBox.scrollHeight;
        }

        function formatSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        async function startScan() {
            document.getElementById('scanBtn').disabled = true;
            document.getElementById('scanSpinner').style.display = 'block';
            document.getElementById('scanStatus').innerText = 'Scanning storages...';
            addLog('Initiating storage scan...');

            try {
                const response = await fetch('/api/scan', { method: 'POST' });
                const data = await response.json();
                
                document.getElementById('scanSpinner').style.display = 'none';
                document.getElementById('scanBtn').disabled = false;
                
                if (data.status === 'success') {
                    document.getElementById('fileCount').innerText = data.count;
                    document.getElementById('scanStatus').innerText = `Found ${data.count} files.`;
                    addLog(`Scan complete. Found ${data.count} files.`);
                    
                    const fileList = document.getElementById('fileList');
                    fileList.innerHTML = '';
                    data.files.slice(0, 100).forEach(file => { // Show max 100 for performance
                        fileList.innerHTML += `
                            <div class="file-item">
                                <span>${file.name}</span>
                                <span style="color: #aaa;">${formatSize(file.size)}</span>
                            </div>`;
                    });
                    if (data.count > 100) {
                        fileList.innerHTML += `<div class="file-item" style="justify-content:center; color: #888;">... and ${data.count - 100} more files</div>`;
                    }
                    
                    document.getElementById('resultsCard').style.display = 'block';
                } else {
                    addLog('Error during scan: ' + data.message);
                }
            } catch (error) {
                addLog('Network error: ' + error);
                document.getElementById('scanSpinner').style.display = 'none';
                document.getElementById('scanBtn').disabled = false;
            }
        }

        async function startMove() {
            document.getElementById('moveBtn').disabled = true;
            document.getElementById('moveSpinner').style.display = 'block';
            document.getElementById('moveStatus').innerText = 'Moving and cleaning files... (Do not close)';
            addLog('Starting safe move and cleanup operation...');

            try {
                const response = await fetch('/api/move', { method: 'POST' });
                const data = await response.json();
                
                document.getElementById('moveSpinner').style.display = 'none';
                
                if (data.status === 'success') {
                    document.getElementById('moveStatus').innerText = `Success! Moved: ${data.moved}, Failed: ${data.failed}`;
                    document.getElementById('moveStatus').style.color = 'var(--success)';
                    addLog(`Operation completed. Moved: ${data.moved}, Failed: ${data.failed}`);
                    document.getElementById('resultsCard').style.display = 'none'; // Hide after success
                } else {
                    document.getElementById('moveStatus').innerText = 'Operation failed.';
                    document.getElementById('moveStatus').style.color = 'red';
                    addLog('Move operation failed.');
                }
            } catch (error) {
                addLog('Network error during move: ' + error);
                document.getElementById('moveSpinner').style.display = 'none';
                document.getElementById('moveBtn').disabled = false;
            }
        }
        
        addLog('System ready. Waiting for user input...');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    try:
        logger.info("Starting API scan request...")
        files = scan_files()
        logger.info(f"Scan complete. Found {len(files)} files.")
        return jsonify({"status": "success", "files": files, "count": len(files)})
    except Exception as e:
        logger.error(f"Scan API error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/move', methods=['POST'])
def api_move():
    try:
        logger.info("Starting API move request...")
        files = scan_files() # Re-scan to ensure we have the latest state
        result = organize_and_clean_files(files)
        logger.info(f"Move complete. Moved: {result['moved']}, Failed: {result['failed']}")
        return jsonify({"status": "success", "moved": result["moved"], "failed": result["failed"]})
    except Exception as e:
        logger.error(f"Move API error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# Entry Point
# ==========================================
if __name__ == "__main__":
    logger.info("Starting Smart Storage Manager Web Server...")
    logger.info("Open your browser and go to: http://127.0.0.1:5000")
    # host='0.0.0.0' allows access from other devices on the same local network (e.g., your PC browser)
    app.run(host='0.0.0.0', port=5000, debug=False)
