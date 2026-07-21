#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║              REPOSITORY GUARDIAN - MAIN CONTROLLER                  ║
║                                                                     ║
║  Unified interface for all security and protection features         ║
║                                                                     ║
║  Author: Danial Zivehdar                                            ║
║  Email: danialzivehdar1992@gmail.com                                ║
║  Date: July 20, 2026                                                ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
from pathlib import Path

# Import core modules
from core.guardian import RepositoryGuardian
from core.security_monitor import RepositorySecurityMonitor
from core.utils import load_config, save_config

class RepositoryGuardianSuite:
    """Unified suite for repository protection and monitoring"""
    
    def __init__(self, config_path='config/config.json'):
        self.config = load_config(config_path)
        self.guardian = None
        self.monitor = None
    
    def initialize_guardian(self, repo_path):
        """Initialize the guardian module"""
        self.guardian = RepositoryGuardian(
            repo_path=repo_path,
            owner_name=self.config.get('owner_name', 'Danial Zivehdar'),
            owner_email=self.config.get('owner_email', 'danialzivehdar1992@gmail.com')
        )
        return self.guardian
    
    def initialize_monitor(self):
        """Initialize the security monitor"""
        if not self.config.get('github_token'):
            print("⚠️  GitHub token not configured. Run: python main.py setup")
            return None
        
        self.monitor = RepositorySecurityMonitor(
            github_token=self.config['github_token'],
            repo_owner=self.config['repo_owner'],
            repo_name=self.config['repo_name'],
            telegram_bot_token=self.config.get('telegram_token'),
            telegram_chat_id=self.config.get('telegram_chat_id')
        )
        return self.monitor
    
    def run(self, action, **kwargs):
        """Run the specified action"""
        actions = {
            'protect': self._action_protect,
            'verify': self._action_verify,
            'scan': self._action_scan,
            'monitor': self._action_monitor,
            'check-logs': self._action_check_logs,
            'report': self._action_report,
            'setup': self._action_setup,
            'status': self._action_status,
        }
        
        if action in actions:
            return actions[action](**kwargs)
        else:
            print(f"Unknown action: {action}")
            return False
    
    def _action_protect(self, repo_path):
        """Protect repository action"""
        guardian = self.initialize_guardian(repo_path)
        return guardian.protect_repository()
    
    def _action_verify(self, repo_path):
        """Verify ownership action"""
        guardian = self.initialize_guardian(repo_path)
        return guardian.verify_ownership()
    
    def _action_scan(self, repo_path):
        """Scan for duplicates action"""
        guardian = self.initialize_guardian(repo_path)
        return guardian.scan_for_duplicates()
    
    def _action_monitor(self):
        """Start monitoring action"""
        monitor = self.initialize_monitor()
        if monitor:
            monitor.monitor_continuous(interval=self.config.get('interval', 300))
    
    def _action_check_logs(self):
        """Check logs action"""
        monitor = self.initialize_monitor()
        if monitor:
            events = monitor.get_recent_activity(hours=24)
            suspicious = monitor.detect_suspicious_activity(events)
            print(f"Recent: {len(events)} | Suspicious: {len(suspicious)}")
    
    def _action_report(self, repo_path=None):
        """Generate report action"""
        if repo_path:
            guardian = self.initialize_guardian(repo_path)
            guardian.generate_legal_report()
        
        monitor = self.initialize_monitor()
        if monitor:
            monitor.generate_security_report()
    
    def _action_setup(self):
        """Setup configuration"""
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║         REPOSITORY GUARDIAN - INITIAL SETUP                ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
        config = {}
        
        config['owner_name'] = input("Owner name [Danial Zivehdar]: ") or "Danial Zivehdar"
        config['owner_email'] = input("Owner email [danialzivehdar1992@gmail.com]: ") or "danialzivehdar1992@gmail.com"
        config['github_token'] = input("GitHub Personal Access Token: ")
        config['repo_owner'] = input("Repository owner: ")
        config['repo_name'] = input("Repository name: ")
        config['telegram_token'] = input("Telegram bot token (optional): ")
        config['telegram_chat_id'] = input("Telegram chat ID (optional): ")
        config['interval'] = int(input("Monitoring interval in seconds [300]: ") or "300")
        
        save_config(config, 'config/config.json')
        print("\n✓ Configuration saved successfully")
    
    def _action_status(self):
        """Show current status"""
        print("\n" + "="*70)
        print("REPOSITORY GUARDIAN STATUS")
        print("="*70)
        print(f"Owner: {self.config.get('owner_name')}")
        print(f"Email: {self.config.get('owner_email')}")
        print(f"Repository: {self.config.get('repo_owner')}/{self.config.get('repo_name')}")
        print(f"Monitoring Interval: {self.config.get('interval')}s")
        print(f"Telegram Alerts: {'✓ Enabled' if self.config.get('telegram_token') else '✗ Disabled'}")
        print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Repository Guardian - Complete Protection Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup                          - Initial setup
  python main.py protect ./my-repo              - Protect repository
  python main.py verify ./my-repo               - Verify ownership
  python main.py monitor                        - Start security monitoring
  python main.py check-logs                     - Check recent activity
  python main.py report ./my-repo               - Generate all reports
  python main.py status                         - Show current status
        """
    )
    
    parser.add_argument('action', 
                       choices=['setup', 'protect', 'verify', 'scan', 'monitor', 
                               'check-logs', 'report', 'status'],
                       help='Action to perform')
    parser.add_argument('repo_path', nargs='?', default='.',
                       help='Repository path (for protect/verify/scan/report)')
    
    args = parser.parse_args()
    
    suite = RepositoryGuardianSuite()
    suite.run(args.action, repo_path=args.repo_path)


if __name__ == "__main__":
    main()
