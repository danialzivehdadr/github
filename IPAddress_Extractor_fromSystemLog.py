#!/usr/bin/env python3
"""
IP Address Extractor from System Logs
Author: Danial Zivehdar
"""

import re
from collections import Counter
from datetime import datetime

def extract_ips_from_logs(log_file):
    """Extract all IP addresses from log files"""
    
    # Common log file locations
    log_paths = [
        '/var/log/auth.log',           # Linux authentication
        '/var/log/syslog',             # Linux system
        '/var/log/apache2/access.log', # Apache web server
        '/var/log/nginx/access.log',   # Nginx web server
        'C:\\Windows\\System32\\winevt\\Logs\\Security.evtx',  # Windows
    ]
    
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    
    all_ips = []
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Find all IPs
            ips = re.findall(ip_pattern, content)
            all_ips.extend(ips)
            
            # Find failed login attempts with IPs
            failed_logins = re.findall(r'Failed password.*?from (\d+\.\d+\.\d+\.\d+)', content)
            
            # Find suspicious connections
            suspicious = re.findall(r'connection from (\d+\.\d+\.\d+\.\d+)', content, re.IGNORECASE)
            
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
    
    return all_ips, failed_logins, suspicious

def analyze_ips(ips):
    """Analyze and rank IP addresses by frequency"""
    ip_counts = Counter(ips)
    
    print("\n" + "="*70)
    print("IP ADDRESS ANALYSIS")
    print("="*70)
    print(f"\nTotal IPs Found: {len(ips)}")
    print(f"Unique IPs: {len(ip_counts)}")
    
    print("\n📊 Top 10 Most Frequent IPs:")
    for i, (ip, count) in enumerate(ip_counts.most_common(10), 1):
        print(f"  {i}. {ip} - {count} occurrences")
    
    return ip_counts

# Usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = '/var/log/auth.log'  # Default Linux log
    
    all_ips, failed_logins, suspicious = extract_ips_from_logs(log_file)
    
    if all_ips:
        ip_counts = analyze_ips(all_ips)
        
        if failed_logins:
            print(f"\n⚠️  Failed Login Attempts:")
            for ip in set(failed_logins):
                count = failed_logins.count(ip)
                print(f"  - {ip}: {count} failed attempts")
        
        if suspicious:
            print(f"\n🔍 Suspicious Connections:")
            for ip in set(suspicious):
                print(f"  - {ip}")
    else:
        print("No IPs found in log file")
