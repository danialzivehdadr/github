#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Malicious Repository Deep Analyzer
Author: Danial Zivehdar
Purpose: Analyze suspicious repository for malware indicators
WARNING: Only run in isolated environment (VM/Sandbox)
"""

import os
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path

class MaliciousRepoAnalyzer:
    """Deep analysis of malicious repositories"""
    
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.findings = []
        
        # Malicious patterns to detect
        self.dangerous_patterns = {
            'data_exfiltration': [
                r'telegram\.bot',
                r'telegram\.api',
                r'discord\.webhook',
                r'ngrok\.io',
                r'webhook\.site',
                r'requestbin',
            ],
            'credential_theft': [
                r'password',
                r'credential',
                r'login',
                r'token',
                r'secret',
                r'api_key',
                r'private_key',
            ],
            'system_access': [
                r'subprocess\.call',
                r'os\.system',
                r'shell=True',
                r'exec\(',
                r'eval\(',
                r'compile\(',
            ],
            'persistence': [
                r'scheduled_task',
                r'startup',
                r'registry',
                r'cron',
                r'systemd',
            ],
            'obfuscation': [
                r'base64\.b64decode',
                r'rot_13',
                r'xor',
                r'encrypt',
                r'decrypt',
            ]
        }
    
    def scan_file(self, filepath):
        """Scan a single file for malicious indicators"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_findings = {
                'file': str(filepath),
                'size': filepath.stat().st_size,
                'hash_md5': self.calculate_hash(filepath),
                'hash_sha256': self.calculate_hash(filepath, 'sha256'),
                'threats': []
            }
            
            # Check for dangerous patterns
            for category, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        file_findings['threats'].append({
                            'category': category,
                            'pattern': pattern,
                            'count': len(matches),
                            'context': self.extract_context(content, pattern)
                        })
            
            # Check file extension
            suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.jar']
            if any(str(filepath).endswith(ext) for ext in suspicious_extensions):
                file_findings['threats'].append({
                    'category': 'suspicious_extension',
                    'pattern': filepath.suffix,
                    'count': 1,
                    'context': 'Executable file found'
                })
            
            if file_findings['threats']:
                self.findings.append(file_findings)
            
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
    
    def extract_context(self, content, pattern, context_chars=100):
        """Extract context around matched pattern"""
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            start = max(0, match.start() - context_chars)
            end = min(len(content), match.end() + context_chars)
            return content[start:end].replace('\n', ' ')
        return ""
    
    def calculate_hash(self, filepath, algorithm='md5'):
        """Calculate file hash"""
        hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def analyze_repository(self):
        """Analyze entire repository"""
        print(f"\n{'='*70}")
        print(f"MALICIOUS REPOSITORY ANALYSIS")
        print(f"{'='*70}")
        print(f"Repository: {self.repo_path}")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Scan all files
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
            
            for file in files:
                filepath = Path(root) / file
                self.scan_file(filepath)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate detailed analysis report"""
        if not self.findings:
            print("✓ No malicious indicators found")
            return
        
        print(f"\n⚠️  THREATS DETECTED: {len(self.findings)} files\n")
        
        for i, finding in enumerate(self.findings, 1):
            print(f"\n{'─'*70}")
            print(f"THREAT #{i}")
            print(f"{'─'*70}")
            print(f"File: {finding['file']}")
            print(f"Size: {finding['size']} bytes")
            print(f"MD5: {finding['hash_md5']}")
            print(f"SHA256: {finding['hash_sha256']}")
            print(f"\nThreats Found:")
            
            for threat in finding['threats']:
                print(f"\n  Category: {threat['category']}")
                print(f"  Pattern: {threat['pattern']}")
                print(f"  Occurrences: {threat['count']}")
                if threat['context']:
                    print(f"  Context: ...{threat['context']}...")
        
        # Save to JSON
        report_data = {
            'analysis_date': datetime.now().isoformat(),
            'repository': str(self.repo_path),
            'total_threats': len(self.findings),
            'findings': self.findings
        }
        
        with open('malicious_repo_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✓ Full report saved to: malicious_repo_report.json")
        print(f"{'='*70}")

# Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyzer = MaliciousRepoAnalyzer(sys.argv[1])
        analyzer.analyze_repository()
    else:
        print("Usage: python malicious_repo_analyzer.py <repository_path>")
