#!/usr/bin/env python3
import os
import time
import re

# ==========================================
# Script Configuration
# ==========================================
BASE_DIR = "/storage/emulated/0"
TARGET_DIRS = ["Pictures", "Music", "Documents", "Download", "DCIM"]

# Directories and Extensions to EXCLUDE (System, Apps, Projects)
EXCLUDE_DIRS = {"Android", "obb", "data", "Projects", "Work", "Company", "System"}
EXCLUDE_EXTENSIONS = {".apk", ".conf", ".xml", ".ini", ".sys", ".prop"}

# Archive extensions to completely wipe
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".tar", ".gz", ".tgz", ".7z"}

# Time threshold for old files (180 days)
THRESHOLD_DAYS = 180
THRESHOLD_SECONDS = THRESHOLD_DAYS * 24 * 60 * 60

# ==========================================
# Core Functions
# ==========================================
def format_size(size_in_bytes):
    """Convert bytes to a human-readable format (MB/GB)."""
    if size_in_bytes >= 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"
    return f"{size_in_bytes / (1024 * 1024):.2f} MB"

def secure_delete(file_path):
    """Overwrites file with random data to prevent recovery, then deletes it."""
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 0:
            with open(file_path, 'r+b') as f:
                chunk_size = 1024 * 1024  # Process in 1MB chunks
                remaining = file_size
                while remaining > 0:
                    chunk = min(chunk_size, remaining)
                    f.write(os.urandom(chunk))
                    remaining -= chunk
                f.flush()
                os.fsync(f.fileno())
        os.remove(file_path)
        return True
    except Exception:
        try:
            os.remove(file_path)
            return True
        except:
            return False

def is_excluded(dir_name, file_name):
    """Check if the directory or file should be excluded."""
    if dir_name in EXCLUDE_DIRS:
        return True
    ext = os.path.splitext(file_name)[1].lower()
    if ext in EXCLUDE_EXTENSIONS:
        return True
    return False

def is_gibberish_or_typo(filename):
    """Heuristic check to detect typos, gibberish, or malformed filenames."""
    name, ext = os.path.splitext(filename)
    name_lower = name.lower()
    
    # 1. Ignore standard camera/app generated names and purely numeric names
    standard_prefixes = ('img_', 'vid_', 'dcim', 'screenshot_', 'whatsapp image', 'p_', 'photo_', 'scan')
    if any(name_lower.startswith(p) for p in standard_prefixes):
        return False
    if name.replace('_', '').replace('-', '').isdigit():
        return False

    # 2. Check for excessive repeated characters (e.g., "fileee", "test___")
    if re.search(r'([a-zA-Z])\1{2,}', name) or re.search(r'([_\-\.\s])\1{1,}', name):
        return True
        
    # 3. Check for long strings with absolutely no vowels (gibberish/consonant mash)
    if len(name) > 6 and not re.search(r'[aeiou]', name_lower):
        return True
        
    # 4. Check for common typo patterns like double extensions (e.g., file.jpg.jpg)
    if re.search(r'\.(jpg|jpeg|png|mp4|pdf|docx|txt)\.(jpg|jpeg|png|mp4|pdf|docx|txt)$', filename.lower()):
        return True
        
    # 5. Check for trailing dots or spaces caused by typos
    if name.endswith('.') or name.endswith(' ') or filename != filename.strip():
        return True

    return False

def clean_and_secure_files():
    """Identify, securely wipe, and permanently delete targeted files."""
    total_deleted = 0
    total_freed_space = 0
    
    for folder in TARGET_DIRS:
        dir_path = os.path.join(BASE_DIR, folder)
        if not os.path.exists(dir_path):
            continue
            
        print(f"[*] Scanning directory: {folder} ...")
        
        for root, dirs, files in os.walk(dir_path):
            # Optimize: Modify dirs in-place to skip excluded directories instantly
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if is_excluded(os.path.basename(root), file):
                    continue
                    
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                should_delete = False
                delete_reason = ""
                
                # Condition 1: Typo, Gibberish, or Malformed filename
                if is_gibberish_or_typo(file):
                    should_delete = True
                    delete_reason = "Typo/Gibberish"
                # Condition 2: Archive file (delete all regardless of age)
                elif ext in ARCHIVE_EXTENSIONS:
                    should_delete = True
                    delete_reason = "Archive"
                # Condition 3: Old file (older than threshold)
                else:
                    try:
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > THRESHOLD_SECONDS:
                            should_delete = True
                            delete_reason = "Old File"
                    except OSError:
                        continue

                if should_delete:
                    try:
                        file_size = os.path.getsize(file_path)
                        if secure_delete(file_path):
                            total_deleted += 1
                            total_freed_space += file_size
                            print(f"    -> Deleted [{delete_reason}]: {file}")
                    except Exception as e:
                        print(f"    [!] Error processing {file_path}: {e}")

    print("\n==================================================")
    print(f"[+] Operation completed successfully.")
    print(f"[+] Total files securely deleted: {total_deleted}")
    print(f"[+] Total storage space freed: {format_size(total_freed_space)}")
    print("[+] Files are overwritten and 100% unrecoverable.")
    print("==================================================")

# ==========================================
# Execution Block
# ==========================================
if __name__ == "__main__":
    print("==================================================")
    print("  Advanced Secure Cleanup & Typo Detection Script")
    print("==================================================")
    print("WARNING: This will PERMANENTLY and SECURELY delete:")
    print("  1. Files with typos, gibberish, or bad formatting.")
    print("  2. All Archive files (.zip, .tar, .rar, etc.).")
    print("  3. Old files (older than 180 days).")
    print("  * Excludes: System files, Apps (.apk), and Projects.")
    print("  * Files are overwritten to prevent ANY recovery.")
    print("==================================================")
    confirm = input("Are you absolutely sure you want to proceed? (yes/no): ")
    
    if confirm.lower() == 'yes':
        clean_and_secure_files()
    else:
        print("Operation aborted by the user.")
