OS_SUPPORT_LINKS = {
    "Windows": {
        "official_support": "https://...",
        # لینک جدید:
        "new_tool": "https://example.com/new-tool",
    },
    # سیستم‌عامل جدید:
    "NewOS": {
        "official_support": "https://...",
    }
}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║                    OS SUPPORT & REPAIR LINKS                       ║
║                                                                    ║
║  A comprehensive collection of direct and official support,        ║
║  update, and repair links for all major operating systems.         ║
║                                                                    ║
║  Author: Danial Zivehdar                                           ║
║  Email: danialzivehdar1992@gmail.com                               ║
║  Date: July 20, 2026                                               ║
║  Version: 1.0.0                                                    ║
║  License: MIT                                                      ║
║                                                                    ║
║  Repository: https://github.com/danialzivehdar/os-support-links    ║
╚══════════════════════════════════════════════════════════════════════╝

USAGE:
    python os_support_links.py              - Display all links
    python os_support_links.py search <kw>  - Search for a specific link
    python os_support_links.py json         - Save all links to JSON
    python os_support_links.py os <name>    - Get links for specific OS
    python os_support_links.py validate     - Validate all links

FEATURES:
    ✓ Direct and official links from trusted sources
    ✓ No external dependencies required
    ✓ Easy to maintain and update
    ✓ Searchable and exportable
    ✓ Link validation support
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION: All OS Support & Repair Links
# ═══════════════════════════════════════════════════════════════════════

OS_SUPPORT_LINKS = {
    "Windows": {
        "official_support": "https://support.microsoft.com/en-us/windows",
        "update_catalog": "https://www.catalog.update.microsoft.com/",
        "media_creation_tool": "https://www.microsoft.com/en-us/software-download/windows11",
        "recovery_tools": "https://support.microsoft.com/en-us/windows/recovery-drivers-in-windows",
        "system_restore": "https://support.microsoft.com/en-us/windows/use-system-restore",
        "troubleshooters": "https://support.microsoft.com/en-us/windows/get-apps-to-fix-problems",
        "safe_mode": "https://support.microsoft.com/en-us/windows/start-your-pc-in-safe-mode",
        "windows_defender": "https://www.microsoft.com/en-us/wdsi/defender",
        "driver_downloads": "https://www.microsoft.com/en-us/download/details.aspx?id=101829"
    },
    
    "macOS": {
        "official_support": "https://support.apple.com/macos",
        "recovery_mode": "https://support.apple.com/guide/mac-help/mchlp1599/mac",
        "disk_utility": "https://support.apple.com/guide/disk-utility/welcome/mac",
        "macos_updates": "https://support.apple.com/en-us/HT201541",
        "startup_disk": "https://support.apple.com/guide/mac-help/mchlp1034/mac",
        "reset_nvram": "https://support.apple.com/en-us/HT204063",
        "reset_smc": "https://support.apple.com/en-us/HT201295",
        "time_machine": "https://support.apple.com/en-us/HT201250",
        "activity_monitor": "https://support.apple.com/guide/activity-monitor/welcome/mac"
    },
    
    "Linux": {
        "Ubuntu": {
            "official_support": "https://ubuntu.com/support",
            "community_help": "https://help.ubuntu.com/",
            "ask_ubuntu": "https://askubuntu.com/",
            "update_manager": "https://help.ubuntu.com/community/Repositories/Ubuntu",
            "recovery_mode": "https://wiki.ubuntu.com/RecoveryMode",
            "terminal_guide": "https://help.ubuntu.com/community/UsingTheTerminal",
            "package_management": "https://help.ubuntu.com/community/AptGet/Howto"
        },
        "Fedora": {
            "official_support": "https://fedoraproject.org/wiki/Getting_help_with_Fedora",
            "ask_fedora": "https://ask.fedoraproject.org/",
            "documentation": "https://docs.fedoraproject.org/",
            "dnf_guide": "https://dnf.readthedocs.io/en/latest/",
            "cockpit": "https://cockpit-project.org/"
        },
        "Debian": {
            "official_support": "https://www.debian.org/support",
            "user_manual": "https://www.debian.org/doc/user-manuals",
            "bug_tracker": "https://bugs.debian.org/",
            "security": "https://www.debian.org/security/",
            "packages": "https://packages.debian.org/"
        },
        "Arch": {
            "official_wiki": "https://wiki.archlinux.org/",
            "forums": "https://bbs.archlinux.org/",
            "aur": "https://aur.archlinux.org/",
            "packages": "https://archlinux.org/packages/"
        }
    },
    
    "Android": {
        "official_support": "https://support.google.com/android",
        "factory_images": "https://developers.google.com/android/images",
        "adb_sdk": "https://developer.android.com/studio/releases/platform-tools",
        "flash_tool": "https://developer.android.com/tools/adb",
        "recovery_mode": "https://support.google.com/android/answer/7680439",
        "ota_updates": "https://source.android.com/docs/setup/start/build-numbers",
        "gsi_images": "https://developer.android.com/topic/generic-system-image",
        "developer_options": "https://developer.android.com/studio/debug/dev-options",
        "security_patches": "https://source.android.com/docs/security/bulletin"
    },
    
    "iOS": {
        "official_support": "https://support.apple.com/ios",
        "recovery_mode": "https://support.apple.com/en-us/HT201263",
        "dfu_mode": "https://support.apple.com/en-us/HT201263",
        "itunes_download": "https://support.apple.com/en-us/HT201319",
        "ipsw_downloads": "https://ipsw.me/",
        "xcode": "https://developer.apple.com/xcode/",
        "apple_configurator": "https://support.apple.com/apple-configurator",
        "testflight": "https://developer.apple.com/testflight/",
        "app_store_connect": "https://appstoreconnect.apple.com/"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN CLASS: OS Support Links Manager
# ═══════════════════════════════════════════════════════════════════════

class OSSupportLinks:
    """Manager for OS support and repair links"""
    
    def __init__(self):
        self.links = OS_SUPPORT_LINKS
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_all_links(self) -> Dict:
        """Return all links"""
        return self.links
    
    def get_os_links(self, os_name: str) -> Optional[Dict]:
        """Get links for a specific operating system"""
        return self.links.get(os_name)
    
    def display_all(self):
        """Display all links in a formatted way"""
        print("\n" + "═"*70)
        print("  OS SUPPORT & REPAIR DIRECT LINKS")
        print(f"  Last Updated: {self.last_updated}")
        print("  Author: Danial Zivehdar")
        print("═"*70)
        
        for os_name, os_data in self.links.items():
            print(f"\n{'─'*70}")
            print(f"  📱 {os_name.upper()}")
            print(f"{'─'*70}")
            
            if isinstance(os_data, dict):
                for category, url in os_data.items():
                    if isinstance(url, str):
                        print(f"  • {category.replace('_', ' ').title()}")
                        print(f"    {url}")
                    elif isinstance(url, dict):
                        print(f"\n  [{category}]")
                        for sub_category, sub_url in url.items():
                            print(f"    • {sub_category.replace('_', ' ').title()}")
                            print(f"      {sub_url}")
    
    def save_to_json(self, filename: str = 'os_support_links.json'):
        """Save all links to a JSON file"""
        data = {
            "metadata": {
                "author": "Danial Zivehdar",
                "email": "danialzivehdar1992@gmail.com",
                "last_updated": self.last_updated,
                "version": "1.0.0",
                "description": "Direct and official support/repair links for all major operating systems"
            },
            "links": self.links
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Links saved to {filename}")
    
    def search_link(self, keyword: str) -> List[Dict]:
        """Search for a specific link by keyword"""
        results = []
        keyword = keyword.lower()
        
        for os_name, os_data in self.links.items():
            if isinstance(os_data, dict):
                for category, url in os_data.items():
                    if isinstance(url, str) and keyword in category.lower():
                        results.append({
                            "os": os_name,
                            "category": category,
                            "url": url
                        })
                    elif isinstance(url, dict):
                        for sub_category, sub_url in url.items():
                            if keyword in sub_category.lower():
                                results.append({
                                    "os": os_name,
                                    "category": f"{category} - {sub_category}",
                                    "url": sub_url
                                })
        
        return results
    
    def validate_all_links(self):
        """Validate all links (requires requests library)"""
        try:
            import requests
        except ImportError:
            print("\n✗ Error: 'requests' library not installed.")
            print("  Install it with: pip install requests")
            return
        
        print("\n" + "═"*70)
        print("  LINK VALIDATION REPORT")
        print("═"*70)
        
        valid_count = 0
        invalid_count = 0
        
        for os_name, os_data in self.links.items():
            print(f"\n📱 {os_name}:")
            
            def check_url(url: str, category: str = ""):
                nonlocal valid_count, invalid_count
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        print(f"  ✓ {category}")
                        valid_count += 1
                    else:
                        print(f"  ✗ {category} (Status: {response.status_code})")
                        invalid_count += 1
                except Exception as e:
                    print(f"  ✗ {category} (Error: {str(e)[:50]})")
                    invalid_count += 1
            
            if isinstance(os_data, dict):
                for category, url in os_data.items():
                    if isinstance(url, str):
                        check_url(url, category)
                    elif isinstance(url, dict):
                        for sub_cat, sub_url in url.items():
                            check_url(sub_url, f"{category}/{sub_cat}")
        
        print("\n" + "═"*70)
        print(f"  ✓ Valid: {valid_count} | ✗ Invalid: {invalid_count}")
        print("═"*70)


# ═══════════════════════════════════════════════════════════════════════
# MAIN FUNCTION: Command Line Interface
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Main function to run the script"""
    os_links = OSSupportLinks()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "search" and len(sys.argv) > 2:
            keyword = " ".join(sys.argv[2:])
            results = os_links.search_link(keyword)
            
            if results:
                print(f"\n🔍 Search results for '{keyword}':")
                for result in results:
                    print(f"\n  OS: {result['os']}")
                    print(f"  Category: {result['category']}")
                    print(f"  URL: {result['url']}")
            else:
                print(f"\n❌ No results found for '{keyword}'")
        
        elif command == "json":
            os_links.save_to_json()
        
        elif command == "os" and len(sys.argv) > 2:
            os_name = sys.argv[2]
            links = os_links.get_os_links(os_name)
            
            if links:
                print(f"\n📱 {os_name.upper()} Links:")
                for category, url in links.items():
                    if isinstance(url, str):
                        print(f"  • {category}: {url}")
                    elif isinstance(url, dict):
                        print(f"\n  [{category}]")
                        for sub_cat, sub_url in url.items():
                            print(f"    • {sub_cat}: {sub_url}")
            else:
                print(f"\n❌ OS '{os_name}' not found")
        
        elif command == "validate":
            os_links.validate_all_links()
        
        else:
            print("\nUsage:")
            print("  python os_support_links.py              - Display all links")
            print("  python os_support_links.py search <kw>  - Search for a link")
            print("  python os_support_links.py json         - Save to JSON file")
            print("  python os_support_links.py os <name>    - Get links for specific OS")
            print("  python os_support_links.py validate     - Validate all links")
    else:
        os_links.display_all()


if __name__ == "__main__":
    main()
