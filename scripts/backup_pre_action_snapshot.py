#!/usr/bin/env python3
"""
scripts/backup_pre_action_snapshot.py
====================================
Universal AI Law 14 Pre-Action Snapshot Protocol.
Creates a lightweight git tag snapshot_pre_ocgis_<timestamp> and atomic .bak
file backups of existing artifacts before state mutation.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def create_pre_action_snapshot() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tag_name = f"snapshot_pre_ocgis_{timestamp}"
    
    print("=" * 70)
    print("UNIVERSAL AI LAW 14: PRE-ACTION STATE PRESERVATION SNAPSHOT")
    print("=" * 70)
    print(f"Target repository: {REPO_ROOT}")
    print(f"Snapshot timestamp: {timestamp} (UTC)")
    print(f"Snapshot git tag:  {tag_name}")
    
    # 1. Create lightweight git tag
    try:
        tag_cmd = ["git", "tag", tag_name]
        res = subprocess.run(tag_cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        print(f"  [✓] Git tag created: {tag_name}")
    except subprocess.CalledProcessError as exc:
        print(f"  [!] Failed to create git tag: {exc.stderr.strip()}", file=sys.stderr)
        # Continue if tag already exists or git error, but note it
    
    # 2. Atomic backup of target files
    files_to_backup = [
        REPO_ROOT / "data" / "ocgis_historical_apn_data.json",
        REPO_ROOT / "scratch" / "ocgis_map_cameron_radius.png",
        REPO_ROOT / "tools" / "ocgis_scraper.py",
    ]
    
    backed_up = []
    for file_path in files_to_backup:
        if file_path.exists():
            bak_path = file_path.with_suffix(file_path.suffix + ".bak")
            try:
                shutil.copy2(file_path, bak_path)
                backed_up.append((file_path, bak_path))
                print(f"  [✓] File backed up: {file_path.relative_to(REPO_ROOT)} -> {bak_path.name}")
            except Exception as e:
                print(f"  [!] Warning backing up {file_path}: {e}", file=sys.stderr)
        else:
            print(f"  [-] File does not exist yet (skipped): {file_path.relative_to(REPO_ROOT)}")
            
    print(f"\n[✓] Universal AI Law 14 snapshot successfully established.")
    print(f"    Total files backed up: {len(backed_up)}")
    print(f"    Git tag: {tag_name}")
    print("=" * 70)

if __name__ == "__main__":
    create_pre_action_snapshot()
