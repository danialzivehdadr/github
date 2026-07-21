#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Security Scanner & Cleaner
Scans and cleans potentially compromised .github repositories

Author: Danial Zivehdar
Date: July 20, 2026
"""

import os
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class GitHubRepoScanner:
    """Scanner for potentially compromised GitHub repositories"""
    
    # Suspicious patterns to look for
    SUSPICIOUS_PATTERNS = [
        'curl',
        'wget',
        'eval(',
        'exec(',
        'base64',
        'nc ',  # netcat
        'bash -i',
        'python -c',
        'powershell',
        'Invoke-WebRequest',
        'Invoke-RestMethod',
        '${{ secrets.',
        'env.',
        'GITHUB_TOKEN',
        'npm publish',
        'pip install',
        'apt-get install',
        'rm -rf',
        '> /dev/tcp',
        'socket',
        'urllib',
        'requests.post',
        'http://',
        'https://'
    ]
    
    SUSPICIOUS_FILE_EXTENSIONS = [
        '.sh',
        '.bash',
        '.ps1',
        '.bat',
        '.cmd',
        '.py',
        '.js',
        '.yml',
        '.yaml'
    ]
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.github_dir = self.repo_path / '.github'
        self.report = []
        self.suspicious_files = []
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan a directory for suspicious files"""
        findings = []
        
        if not directory.exists():
            return findings
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                if self.is_suspicious_file(file_path):
                    finding = self.analyze_file(file_path)
                    if finding['suspicious']:
                        findings.append(finding)
        
        return findings
    
    def is_suspicious_file(self, file_path: Path) -> bool:
        """Check if file extension is suspicious"""
        return file_path.suffix.lower() in self.SUSPICIOUS_FILE_EXTENSIONS
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a file for suspicious content"""
        result = {
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'suspicious': False,
            'findings': [],
            'hash': self.calculate_hash(file_path)
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for pattern in self.SUSPICIOUS_PATTERNS:
                    if pattern in content:
                        result['findings'].append(f"Found suspicious pattern: '{pattern}'")
                        result['suspicious'] = True
                
                # Check for secrets exposure
                if 'secrets.' in content.lower():
                    result['findings'].append("Potential secrets exposure detected")
                    result['suspicious'] = True
                
                # Check for obfuscated content
                if len(content) > 0:
                    entropy = self.calculate_entropy(content)
                    if entropy > 5.0:
                        result['findings'].append(f"High entropy detected: {entropy:.2f} (possible obfuscation)")
                        result['suspicious'] = True
        
        except Exception as e:
            result['findings'].append(f"Error reading file: {str(e)}")
        
        return result
    
    def calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calculate_entropy(self, data: str) -> float:
        """Calculate entropy of data"""
        from collections import Counter
        import math
        
        if not data:
            return 0.0
        
        counter = Counter(data)
        entropy = 0.0
        for count in counter.values():
            probability = count / len(data)
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def check_github_actions(self) -> List[Dict]:
        """Check GitHub Actions workflows"""
        workflows_dir = self.github_dir / 'workflows'
        findings = []
        
        if workflows_dir.exists():
            for workflow in workflows_dir.glob('*.yml'):
                analysis = self.analyze_file(workflow)
                
                # Additional checks for workflows
                try:
                    with open(workflow, 'r') as f:
                        content = yaml.safe_load(f)
                    
                    # Check for dangerous permissions
                    if content.get('permissions') == 'write-all':
                        analysis['findings'].append("Dangerous permission: write-all")
                        analysis['suspicious'] = True
                    
                    # Check for on: push to main
                    if 'on' in content:
                        if 'push' in content['on']:
                            if 'branches' in content['on']['push']:
                                if 'main' in content['on']['push']['branches'] or 'master' in content['on']['push']['branches']:
                                    analysis['findings'].append("Triggers on push to main/master")
                    
                    findings.append(analysis)
                except Exception as e:
                    analysis['findings'].append(f"Error parsing YAML: {str(e)}")
                    findings.append(analysis)
        
        return findings
    
    def generate_report(self, output_file: str = 'security_report.json'):
        """Generate comprehensive security report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'repository_path': str(self.repo_path),
            'github_dir_exists': self.github_dir.exists(),
            'findings': [],
            'summary': {
                'total_suspicious_files': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0
            }
        }
        
        # Scan all directories
        findings = self.scan_directory(self.github_dir)
        
        # Check GitHub Actions
        action_findings = self.check_github_actions()
        findings.extend(action_findings)
        
        report['findings'] = findings
        
        # Calculate summary
        for finding in findings:
            report['summary']['total_suspicious_files'] += 1
            if len(finding['findings']) > 3:
                report['summary']['high_risk'] += 1
            elif len(finding['findings']) > 1:
                report['summary']['medium_risk'] += 1
            else:
                report['summary']['low_risk'] += 1
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.print_report(report)
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted report"""
        print("\n" + "="*70)
        print("  GITHUB REPOSITORY SECURITY SCAN REPORT")
        print("="*70)
        print(f"  Scan Date: {report['scan_date']}")
        print(f"  Repository: {report['repository_path']}")
        print(f"  .github exists: {report['github_dir_exists']}")
        print("\n" + "-"*70)
        print("  SUMMARY")
        print("-"*70)
        print(f"  Total Suspicious Files: {report['summary']['total_suspicious_files']}")
        print(f"  🔴 High Risk: {report['summary']['high_risk']}")
        print(f"  🟡 Medium Risk: {report['summary']['medium_risk']}")
        print(f"  🟢 Low Risk: {report['summary']['low_risk']}")
        
        if report['findings']:
            print("\n" + "-"*70)
            print("  FINDINGS")
            print("-"*70)
            
            for i, finding in enumerate(report['findings'], 1):
                print(f"\n  [{i}] {finding['path']}")
                print(f"      Size: {finding['size']} bytes")
                print(f"      Modified: {finding['modified']}")
                print(f"      Hash: {finding['hash'][:16]}...")
                
                for f in finding['findings']:
                    print(f"      ⚠️  {f}")
        
        print("\n" + "="*70)
    
    def clean_repository(self):
        """Clean the repository (DANGEROUS - use with caution)"""
        print("\n" + "!"*70)
        print("  WARNING: This will delete suspicious files!")
        print("!"*70)
        
        response = input("\n  Are you sure you want to proceed? (yes/no): ")
        
        if response.lower() == 'yes':
            cleaned = []
            
            for finding in self.scan_directory(self.github_dir):
                if finding['suspicious']:
                    try:
                        file_path = Path(finding['path'])
                        file_path.unlink()
                        cleaned.append(str(file_path))
                        print(f"  ✓ Deleted: {file_path}")
                    except Exception as e:
                        print(f"  ✗ Error deleting {finding['path']}: {e}")
            
            print(f"\n  ✓ Cleaned {len(cleaned)} files")
            return cleaned
        else:
            print("\n  ✗ Operation cancelled")
            return []


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python github_scanner.py <repository_path> [clean]")
        print("\nExamples:")
        print("  python github_scanner.py /path/to/repo")
        print("  python github_scanner.py /path/to/repo clean")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    if not os.path.exists(repo_path):
        print(f"Error: Repository path '{repo_path}' does not exist")
        sys.exit(1)
    
    scanner = GitHubRepoScanner(repo_path)
    
    if len(sys.argv) > 2 and sys.argv[2] == 'clean':
        scanner.generate_report()
        scanner.clean_repository()
    else:
        scanner.generate_report()


if __name__ == "__main__":
    main()
