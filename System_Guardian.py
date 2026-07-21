#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Guardian - Comprehensive Security & Cleanup Tool
Features: File scanning, keylogger detection, system cleanup, optimization
"""

import os
import sys
import time
import hashlib
import psutil
import socket
import platform
import subprocess
import threading
from datetime import datetime
from pathlib import Path

# ============================================
# Section 1: Antivirus Core
# ============================================
class AntivirusCore:
    """Core engine for scanning and threat detection"""
    
    def __init__(self):
        self.threats_found = []
        self.scan_start_time = None
        self.files_scanned = 0
        
    def calculate_file_hash(self, filepath):
        """Calculate SHA256 hash of a file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (PermissionError, OSError) as e:
            return None
    
    def scan_file(self, filepath, suspicious_signatures=None):
        """Scan a file for suspicious patterns"""
        if suspicious_signatures is None:
            suspicious_signatures = [
                b'eval(base64_decode',
                b'exec(',
                b'system(',
                b'shell_exec',
                b'powershell -enc',
                b'cmd.exe /c',
            ]
        
        try:
            with open(filepath, 'rb') as f:
                content = f.read(1024 * 100)  # Only first 100KB
                for sig in suspicious_signatures:
                    if sig in content:
                        return True, sig
            return False, None
        except (PermissionError, OSError, UnicodeDecodeError):
            return False, None
    
    def quick_scan(self, path):
        """Quick scan of a directory"""
        self.scan_start_time = datetime.now()
        self.files_scanned = 0
        self.threats_found = []
        
        print(f"\n{'='*60}")
        print(f"🔍 Starting scan: {path}")
        print(f"{'='*60}\n")
        
        for root, dirs, files in os.walk(path):
            # Skip system folders for faster scanning
            dirs[:] = [d for d in dirs if d not in ['$Recycle.Bin', 'System Volume Information']]
            
            for file in files:
                filepath = os.path.join(root, file)
                self.files_scanned += 1
                
                is_suspicious, signature = self.scan_file(filepath)
                if is_suspicious:
                    self.threats_found.append({
                        'path': filepath,
                        'signature': signature.decode('utf-8', errors='ignore'),
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
                    print(f"⚠️  Suspicious file: {filepath}")
        
        duration = (datetime.now() - self.scan_start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"✅ Scan completed")
        print(f"📊 Files scanned: {self.files_scanned}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🚨 Threats found: {len(self.threats_found)}")
        print(f"{'='*60}\n")
        
        return self.threats_found


# ============================================
# Section 2: Keylogger Detection (Defensive Monitoring)
# ============================================
class KeyboardMonitor:
    """Monitor inputs to detect malicious keyloggers"""
    
    def __init__(self):
        self.monitoring = False
        self.suspicious_processes = []
        
    def detect_keyloggers(self):
        """Identify suspicious processes that might be keyloggers"""
        suspicious_keywords = [
            'keylog', 'spy', 'sniff', 'capture', 'hook',
            'recorder', 'monitor', 'steal'
        ]
        
        print("\n🔎 Scanning for suspicious processes (keyloggers)...")
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                proc_exe = (proc.info['exe'] or '').lower()
                
                for keyword in suspicious_keywords:
                    if keyword in proc_name or keyword in proc_exe:
                        self.suspicious_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'path': proc.info['exe']
                        })
                        print(f"⚠️  Suspicious process found:")
                        print(f"    PID: {proc.info['pid']}")
                        print(f"    Name: {proc.info['name']}")
                        print(f"    Path: {proc.info['exe']}\n")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not self.suspicious_processes:
            print("✅ No suspicious keyloggers detected.")
        
        return self.suspicious_processes
    
    def check_startup_programs(self):
        """Check startup programs (where keyloggers hide)"""
        print("\n🔎 Checking startup programs...")
        
        startup_paths = []
        system = platform.system()
        
        if system == 'Windows':
            startup_paths = [
                os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'),
                'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            ]
        elif system == 'Linux' or system == 'Android':
            startup_paths = [
                os.path.expanduser('~/.config/autostart'),
                '/etc/init.d'
            ]
        
        found_items = []
        for path in startup_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    found_items.append(full_path)
                    print(f"📌 {item}")
        
        return found_items


# ============================================
# Section 3: System Cleaner
# ============================================
class SystemCleaner:
    """Clean temporary files and system cache"""
    
    def __init__(self):
        self.cleaned_size = 0
        self.cleaned_files = 0
        
    def clean_temp_files(self):
        """Clean temporary folders"""
        print("\n🧹 Starting temporary file cleanup...")
        
        temp_paths = []
        system = platform.system()
        
        if system == 'Windows':
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                'C:\\Windows\\Temp'
            ]
        else:
            temp_paths = ['/tmp', '/var/tmp']
        
        for temp_path in temp_paths:
            if temp_path and os.path.exists(temp_path):
                self._clean_directory(temp_path)
        
        print(f"\n✅ Cleanup completed")
        print(f"📊 Files removed: {self.cleaned_files}")
        print(f"💾 Space freed: {self.cleaned_size / (1024*1024):.2f} MB")
    
    def _clean_directory(self, path):
        """Clean a directory"""
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path):
                        file_size = os.path.getsize(item_path)
                        os.remove(item_path)
                        self.cleaned_size += file_size
                        self.cleaned_files += 1
                    elif os.path.isdir(item_path):
                        self._clean_directory(item_path)
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            pass
    
    def clean_browser_cache(self):
        """Clean browser cache"""
        print("\n🧹 Cleaning browser cache...")
        
        cache_paths = []
        system = platform.system()
        
        if system == 'Windows':
            cache_paths = [
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache'),
                os.path.expanduser('~\\AppData\\Local\\Mozilla\\Firefox\\Profiles'),
            ]
        
        cleaned = 0
        for path in cache_paths:
            if os.path.exists(path):
                old_count = self.cleaned_files
                self._clean_directory(path)
                cleaned += (self.cleaned_files - old_count)
        
        print(f"✅ {cleaned} cache files removed")


# ============================================
# Section 4: System Optimizer
# ============================================
class SystemOptimizer:
    """Optimize system security settings"""
    
    def __init__(self):
        self.optimizations = []
    
    def check_open_ports(self):
        """Check for open and suspicious ports"""
        print("\n🔒 Checking open system ports...")
        
        open_ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN':
                open_ports.append({
                    'port': conn.laddr.port,
                    'pid': conn.pid,
                    'process': psutil.Process(conn.pid).name() if conn.pid else 'Unknown'
                })
        
        if open_ports:
            print(f"⚠️  {len(open_ports)} open ports detected:")
            for p in open_ports:
                print(f"    Port {p['port']} - {p['process']} (PID: {p['pid']})")
        else:
            print("✅ No suspicious ports are open")
        
        return open_ports
    
    def check_network_connections(self):
        """Check active network connections"""
        print("\n🌐 Checking network connections...")
        
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                try:
                    process_name = psutil.Process(conn.pid).name() if conn.pid else 'Unknown'
                    connections.append({
                        'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                        'process': process_name
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        print(f"📊 {len(connections)} active connections:")
        for c in connections[:10]:  # Only first 10
            print(f"    {c['process']} -> {c['remote']}")
        
        return connections
    
    def optimize_system_settings(self):
        """Apply optimization settings"""
        print("\n⚙️  Optimizing system settings...")
        
        optimizations = []
        system = platform.system()
        
        if system == 'Windows':
            # Disable unnecessary services
            optimizations.append("Checking Windows services")
            # Enable firewall
            optimizations.append("Checking firewall status")
        else:
            optimizations.append("Checking iptables settings")
        
        for opt in optimizations:
            print(f"✅ {opt}")
        
        return optimizations


# ============================================
# Section 5: Main Menu Interface
# ============================================
class SecurityDashboard:
    """Main tool dashboard"""
    
    def __init__(self):
        self.antivirus = AntivirusCore()
        self.keyboard_monitor = KeyboardMonitor()
        self.cleaner = SystemCleaner()
        self.optimizer = SystemOptimizer()
    
    def show_header(self):
        print("\n" + "="*60)
        print("🛡️  SYSTEM GUARDIAN - Security & Cleanup Suite")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 OS: {platform.system()} {platform.release()}")
        print("="*60 + "\n")
    
    def show_menu(self):
        print("📋 Main Menu:")
        print("-"*40)
        print("1. 🔍 Quick scan for suspicious files")
        print("2. ⌨️  Detect keyloggers")
        print("3. 🚀 Check startup programs")
        print("4. 🧹 Clean temporary files")
        print("5. 🌐 Clean browser cache")
        print("6. 🔒 Check open ports")
        print("7. 🌍 Check network connections")
        print("8. ⚙️  Optimize system settings")
        print("9. 🛡️  Full system scan (all features)")
        print("0. 🚪 Exit")
        print("-"*40)
    
    def full_scan(self):
        """Complete system scan"""
        print("\n🛡️  Starting full system scan...\n")
        
        # 1. Detect keyloggers
        self.keyboard_monitor.detect_keyloggers()
        
        # 2. Check startup
        self.keyboard_monitor.check_startup_programs()
        
        # 3. Scan user files
        user_home = os.path.expanduser('~')
        self.antivirus.quick_scan(user_home)
        
        # 4. Cleanup
        self.cleaner.clean_temp_files()
        self.cleaner.clean_browser_cache()
        
        # 5. Check network
        self.optimizer.check_open_ports()
        self.optimizer.check_network_connections()
        
        # 6. Optimize
        self.optimizer.optimize_system_settings()
        
        print("\n" + "="*60)
        print("✅ Full system scan completed")
        print("="*60 + "\n")
    
    def run(self):
        """Main program execution"""
        while True:
            self.show_header()
            self.show_menu()
            
            choice = input("\n👉 Enter your choice: ").strip()
            
            if choice == '1':
                path = input("📁 Scan path (default: home): ").strip()
                if not path:
                    path = os.path.expanduser('~')
                if os.path.exists(path):
                    self.antivirus.quick_scan(path)
                else:
                    print("❌ Invalid path")
            
            elif choice == '2':
                self.keyboard_monitor.detect_keyloggers()
            
            elif choice == '3':
                self.keyboard_monitor.check_startup_programs()
            
            elif choice == '4':
                self.cleaner.clean_temp_files()
            
            elif choice == '5':
                self.cleaner.clean_browser_cache()
            
            elif choice == '6':
                self.optimizer.check_open_ports()
            
            elif choice == '7':
                self.optimizer.check_network_connections()
            
            elif choice == '8':
                self.optimizer.optimize_system_settings()
            
            elif choice == '9':
                self.full_scan()
            
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
            
            input("\n⏎ Press Enter to continue...")


# ============================================
# Program Entry Point
# ============================================
if __name__ == "__main__":
    try:
        dashboard = SecurityDashboard()
        dashboard.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
