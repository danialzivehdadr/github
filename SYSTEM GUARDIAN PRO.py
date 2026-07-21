#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Guardian Pro - Owner-Level Security Suite
Cross-platform (Windows/Android/Linux)
Features: Download scanner, crash detection, factory reset
"""

import os
import sys
import hashlib
import json
import shutil
import subprocess
import platform
import psutil
from pathlib import Path
from datetime import datetime
import sqlite3
import logging

# ============================================
# Configuration & Logging
# ============================================
LOG_FILE = "system_guardian.log"
DB_FILE = "guardian.db"
DOWNLOAD_DIRS = {
    'Windows': [os.path.expanduser('~\\Downloads')],
    'Linux': [os.path.expanduser('~/Downloads')],
    'Android': ['/sdcard/Download', '/storage/emulated/0/Download']
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# Database Manager
# ============================================
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self._init_db()
    
    def _init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scanned_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT UNIQUE,
                hash_sha256 TEXT,
                status TEXT,
                scan_date TEXT,
                threat_type TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TEXT,
                registry_backup TEXT,
                config_backup TEXT
            )
        ''')
        self.conn.commit()
    
    def log_file_scan(self, filepath, file_hash, status, threat_type=None):
        self.cursor.execute('''
            INSERT OR REPLACE INTO scanned_files 
            (filepath, hash_sha256, status, scan_date, threat_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (filepath, file_hash, status, datetime.now().isoformat(), threat_type))
        self.conn.commit()
    
    def is_file_scanned(self, filepath):
        self.cursor.execute('SELECT status FROM scanned_files WHERE filepath = ?', (filepath,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        self.conn.close()

# ============================================
# File Scanner & Analyzer
# ============================================
class FileScanner:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.suspicious_extensions = [
            '.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.scr',
            '.com', '.pif', '.hta', '.cpl', '.msc', '.jar'
        ]
        self.dangerous_signatures = [
            b'MZ',  # PE executable
            b'PK',  # ZIP (could be malicious)
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec',
            b'powershell -enc',
            b'cmd.exe /c',
            b'wget ',
            b'curl ',
            b'base64_decode'
        ]
    
    def calculate_hash(self, filepath):
        try:
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed for {filepath}: {e}")
            return None
    
    def scan_file(self, filepath):
        """Deep scan a single file"""
        if not os.path.exists(filepath):
            return None
        
        # Check if already scanned
        cached_status = self.db.is_file_scanned(filepath)
        if cached_status:
            return cached_status
        
        file_hash = self.calculate_hash(filepath)
        if not file_hash:
            return "ERROR"
        
        # Check extension
        ext = os.path.splitext(filepath)[1].lower()
        if ext in self.suspicious_extensions:
            self.db.log_file_scan(filepath, file_hash, "SUSPICIOUS", "Executable")
            return "SUSPICIOUS"
        
        # Check signatures
        try:
            with open(filepath, 'rb') as f:
                header = f.read(1024)
                for sig in self.dangerous_signatures:
                    if sig in header:
                        self.db.log_file_scan(filepath, file_hash, "THREAT", f"Signature:{sig}")
                        return "THREAT"
        except Exception as e:
            logger.error(f"Scan failed for {filepath}: {e}")
            self.db.log_file_scan(filepath, file_hash, "ERROR", str(e))
            return "ERROR"
        
        # Check file size (too large or too small)
        file_size = os.path.getsize(filepath)
        if file_size > 500 * 1024 * 1024:  # 500MB
            self.db.log_file_scan(filepath, file_hash, "WARNING", "LargeFile")
            return "WARNING"
        
        self.db.log_file_scan(filepath, file_hash, "CLEAN")
        return "CLEAN"
    
    def scan_downloads(self):
        """Scan all download directories"""
        system = platform.system()
        download_dirs = DOWNLOAD_DIRS.get(system, DOWNLOAD_DIRS['Linux'])
        
        results = {"CLEAN": 0, "SUSPICIOUS": 0, "THREAT": 0, "ERROR": 0, "WARNING": 0}
        
        for download_dir in download_dirs:
            if not os.path.exists(download_dir):
                continue
            
            logger.info(f"Scanning: {download_dir}")
            
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    status = self.scan_file(filepath)
                    if status:
                        results[status] += 1
                        if status in ["THREAT", "SUSPICIOUS"]:
                            logger.warning(f"⚠️  {status}: {filepath}")
        
        logger.info(f"Scan complete: {results}")
        return results

# ============================================
# System Crash Detector
# ============================================
class CrashDetector:
    def __init__(self):
        self.crash_logs = []
    
    def check_recent_crashes(self):
        """Check for recent system crashes"""
        system = platform.system()
        crashes = []
        
        if system == 'Windows':
            try:
                # Check Windows Event Viewer for critical errors
                cmd = 'wevtutil qe System /q:"*[System[Level=1 or Level=2]]" /c:10 /rd:true /f:text'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    crashes.append(result.stdout)
            except Exception as e:
                logger.error(f"Windows crash check failed: {e}")
        
        elif system == 'Linux' or system == 'Android':
            try:
                # Check dmesg for kernel panics
                cmd = 'dmesg | grep -i "error\\|panic\\|fail" | tail -20'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    crashes.append(result.stdout)
            except Exception as e:
                logger.error(f"Linux crash check failed: {e}")
        
        return crashes
    
    def identify_problematic_files(self):
        """Identify files that may have caused crashes"""
        problematic = []
        
        # Check recently modified executables
        for download_dir in DOWNLOAD_DIRS.get(platform.system(), []):
            if not os.path.exists(download_dir):
                continue
            
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(filepath)
                        # Files modified in last 24 hours
                        if datetime.now().timestamp() - mtime < 86400:
                            ext = os.path.splitext(filepath)[1].lower()
                            if ext in ['.exe', '.dll', '.so', '.apk']:
                                problematic.append({
                                    'path': filepath,
                                    'modified': datetime.fromtimestamp(mtime).isoformat()
                                })
                    except Exception:
                        continue
        
        return problematic

# ============================================
# Factory Reset Manager
# ============================================
class FactoryReset:
    def __init__(self):
        self.backup_dir = Path("system_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self):
        """Create system configuration backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir()
        
        system = platform.system()
        
        if system == 'Windows':
            # Backup registry
            try:
                reg_backup = backup_path / "registry.reg"
                cmd = f'reg export HKLM {reg_backup} /y'
                subprocess.run(cmd, shell=True, check=True)
                logger.info("Registry backed up")
            except Exception as e:
                logger.error(f"Registry backup failed: {e}")
        
        # Backup user configurations
        config_dirs = {
            'Windows': [os.path.expanduser('~\\AppData\\Roaming')],
            'Linux': [os.path.expanduser('~/.config')],
            'Android': ['/sdcard/Android/data']
        }
        
        for config_dir in config_dirs.get(system, []):
            if os.path.exists(config_dir):
                try:
                    shutil.copytree(config_dir, backup_path / "config_backup", 
                                  ignore=shutil.ignore_patterns('*.log', '*.tmp'))
                    logger.info(f"Config backed up: {config_dir}")
                except Exception as e:
                    logger.error(f"Config backup failed: {e}")
        
        return backup_path
    
    def reset_to_factory(self, backup_path=None):
        """Reset system to factory settings"""
        logger.warning("⚠️  FACTORY RESET INITIATED")
        
        system = platform.system()
        
        if system == 'Windows':
            # Reset Windows settings
            try:
                # Reset network
                subprocess.run('netsh winsock reset', shell=True)
                subprocess.run('netsh int ip reset', shell=True)
                logger.info("Network settings reset")
                
                # Clear temp files
                temp_dirs = [os.environ.get('TEMP'), 'C:\\Windows\\Temp']
                for temp_dir in temp_dirs:
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("Temp files cleared")
                
                # Reset firewall
                subprocess.run('netsh advfirewall reset', shell=True)
                logger.info("Firewall reset")
                
            except Exception as e:
                logger.error(f"Windows reset failed: {e}")
        
        elif system in ['Linux', 'Android']:
            try:
                # Clear package cache
                subprocess.run('apt-get clean', shell=True)
                subprocess.run('apt-get autoremove -y', shell=True)
                
                # Clear temp
                subprocess.run('rm -rf /tmp/*', shell=True)
                subprocess.run('rm -rf /var/tmp/*', shell=True)
                
                logger.info("Linux system cleaned")
                
            except Exception as e:
                logger.error(f"Linux reset failed: {e}")
        
        logger.info("✅ Factory reset completed")
        return True

# ============================================
# Main Controller
# ============================================
class SystemGuardianPro:
    def __init__(self):
        self.db = DatabaseManager()
        self.scanner = FileScanner(self.db)
        self.crash_detector = CrashDetector()
        self.factory_reset = FactoryReset()
    
    def show_menu(self):
        print("\n" + "="*60)
        print("🛡️  SYSTEM GUARDIAN PRO - Owner-Level Edition")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 {platform.system()} {platform.release()}")
        print("="*60)
        print("\n📋 Main Menu:")
        print("-"*40)
        print("1. 🔍 Scan all downloads")
        print("2. 💥 Check system crashes")
        print("3. 🎯 Identify problematic files")
        print("4. 💾 Create system backup")
        print("5. 🏭 Factory reset system")
        print("6. 📊 View scan history")
        print("0. 🚪 Exit")
        print("-"*40)
    
    def run(self):
        while True:
            self.show_menu()
            choice = input("\n👉 Enter choice: ").strip()
            
            if choice == '1':
                results = self.scanner.scan_downloads()
                print(f"\n✅ Scan complete: {results}")
            
            elif choice == '2':
                crashes = self.crash_detector.check_recent_crashes()
                if crashes:
                    print("\n💥 Recent crashes detected:")
                    for crash in crashes:
                        print(crash)
                else:
                    print("\n✅ No recent crashes found")
            
            elif choice == '3':
                problematic = self.crash_detector.identify_problematic_files()
                if problematic:
                    print("\n🎯 Problematic files:")
                    for p in problematic:
                        print(f"  {p['path']} (modified: {p['modified']})")
                else:
                    print("\n✅ No problematic files found")
            
            elif choice == '4':
                backup_path = self.factory_reset.create_backup()
                print(f"\n💾 Backup created: {backup_path}")
            
            elif choice == '5':
                confirm = input("\n⚠️  This will reset system to factory settings. Continue? (yes/no): ")
                if confirm.lower() == 'yes':
                    self.factory_reset.create_backup()
                    self.factory_reset.reset_to_factory()
                else:
                    print("❌ Cancelled")
            
            elif choice == '6':
                self.db.cursor.execute('SELECT filepath, status, scan_date FROM scanned_files ORDER BY scan_date DESC LIMIT 20')
                rows = self.db.cursor.fetchall()
                print("\n📊 Recent scan history:")
                for row in rows:
                    print(f"  {row[0]} - {row[1]} ({row[2]})")
            
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            
            input("\n⏎ Press Enter to continue...")
        
        self.db.close()

# ============================================
# Entry Point
# ============================================
if __name__ == "__main__":
    try:
        guardian = SystemGuardianPro()
        guardian.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
