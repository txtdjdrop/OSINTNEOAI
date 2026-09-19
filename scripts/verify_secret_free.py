#!/usr/bin/env python3
"""
scripts/verify_secret_free.py
=============================
Pre-Commit Secret Defense Engine for OsintNeoAi.
Scans tracked, staged, and candidate files for unredacted credentials, API keys,
private keys, GCP service account credentials, AWS/Azure tokens, and JWTs.

Exit Codes:
  0: Clean, zero secrets found.
  1: Secret violation detected (commit must be aborted).
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]

# Dynamic construction to prevent self-matching
SECRET_PATTERNS = {
    "Google / Gemini API Key": re.compile(r"\bAI" + r"za[0-9A-Za-z\-_]{35,40}\b"),
    "Private Key Block": re.compile(r"-----BEGIN " + r"[A-Z0-9_\s]*PRIVATE KEY-----"),
    "JSON Web Token (JWT)": re.compile(r"\beyJ" + r"[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"),
    "GCP Service Account": re.compile(r'"type"\s*:\s*"service_' + r'account"'),
    "AWS Access Key": re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)" + r"[0-9A-Z]{16}\b"),
    "Azure Connection Key": re.compile(r"AccountKey=" + r"[A-Za-z0-9+/=]{86,88}"),
    "Azure Storage Connection String": re.compile(r"DefaultEndpointsProtocol=" + r"https;AccountName="),
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz",
    ".exe", ".dll", ".so", ".bin", ".pyc", ".db", ".sqlite", ".bak"
}

WHITELISTED_PATHS = {
    "scripts/verify_secret_free.py",
    "tests/test_ocgis_scraper_e2e.py",
    "scripts/scan_and_rotate_api_keys.py",
}

EXCLUDED_DIRS_AND_FILES = {
    "data/chats",
    "data/gcp_console_extraction.json",
    "data/all_extracted_bookmarks.json",
    "data/edr_apn_historical_data.json",
    "data/oc_land_insights",
}

def is_binary_file(file_path: Path) -> bool:
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with open(file_path, "rb") as fp:
            chunk = fp.read(1024)
            if b"\0" in chunk:
                return True
    except Exception:
        return True
    return False

def scan_text_content(content: str, rel_path: str) -> List[Tuple[int, str, str]]:
    """Scan string content line-by-line for secret patterns."""
    violations = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Ignore comments or test fixtures with explicit redaction markers
        if any(marker in line for marker in ["REDACTED", "placeholder"]):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            match = pattern.search(line)
            if match:
                snippet = line.strip()
                if len(snippet) > 80:
                    snippet = snippet[:77] + "..."
                violations.append((idx, name, snippet))
    return violations

def scan_file(file_path: Path) -> List[Tuple[int, str, str]]:
    rel_path = file_path.relative_to(REPO_ROOT).as_posix()
    if rel_path in WHITELISTED_PATHS:
        return []
    for excluded in EXCLUDED_DIRS_AND_FILES:
        if rel_path == excluded or rel_path.startswith(excluded + "/"):
            return []
    if is_binary_file(file_path):
        return []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Warning: could not read {rel_path}: {e}", file=sys.stderr)
        return []
    return scan_file_content(content, rel_path)

def scan_file_content(content: str, rel_path: str) -> List[Tuple[int, str, str]]:
    return scan_text_content(content, rel_path)

def scan_staged_diff() -> List[Tuple[str, int, str, str]]:
    """Scan git staged changes via git diff --cached."""
    res = subprocess.run(
        ["git", "diff", "--cached", "-U0"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    if res.returncode != 0:
        return []
    
    current_file = ""
    violations = []
    line_number = 0
    
    for line in res.stdout.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            line_number = 0
            continue
        elif line.startswith("@@"):
            # @@ -0,0 +1,5 @@
            m = re.search(r"\+(\d+)", line)
            if m:
                line_number = int(m.group(1))
            continue
        elif line.startswith("+") and not line.startswith("+++"):
            added_line = line[1:]
            if current_file in WHITELISTED_PATHS:
                line_number += 1
                continue
            if any(marker in added_line for marker in ["REDACTED", "placeholder"]):
                line_number += 1
                continue
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(added_line):
                    snippet = added_line.strip()
                    if len(snippet) > 80:
                        snippet = snippet[:77] + "..."
                    violations.append((current_file, line_number, name, snippet))
            line_number += 1
    return violations

def main() -> None:
    print("=" * 70)
    print("OSINTNEOAI PRE-COMMIT SECRET DEFENSE SCANNER")
    print("=" * 70)
    print(f"Repository Root: {REPO_ROOT}")
    
    targets = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            p = Path(arg)
            if not p.is_absolute():
                p = REPO_ROOT / p
            if p.exists() and p.is_file():
                targets.append(p)
    
    violations_found = 0
    
    if targets:
        print(f"Scanning {len(targets)} explicitly provided files...")
        for p in targets:
            v = scan_file(p)
            if v:
                rel = p.relative_to(REPO_ROOT).as_posix()
                for lnum, sname, snip in v:
                    print(f"🚨 [VIOLATION] {rel}:{lnum} - {sname} -> {snip}")
                    violations_found += 1
    else:
        # Check staged files first
        res_staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        staged_files = [line.strip() for line in res_staged.stdout.splitlines() if line.strip()]
        
        if staged_files:
            print(f"Scanning {len(staged_files)} staged files in git index...")
            for rel in staged_files:
                p = REPO_ROOT / rel
                if p.exists() and p.is_file():
                    v = scan_file(p)
                    if v:
                        for lnum, sname, snip in v:
                            print(f"🚨 [STAGED VIOLATION] {rel}:{lnum} - {sname} -> {snip}")
                            violations_found += 1
        else:
            # Check git status modified/untracked files or deliverable files
            deliverables = [
                REPO_ROOT / "scripts" / "backup_pre_action_snapshot.py",
                REPO_ROOT / "scripts" / "verify_secret_free.py",
                REPO_ROOT / "scripts" / "run_ocgis_spatial_scraper.py",
                REPO_ROOT / "data" / "ocgis_historical_apn_data.json",
            ]
            candidates = [f for f in deliverables if f.exists()]
            print(f"No files currently staged. Scanning {len(candidates)} deliverable files...")
            for p in candidates:
                v = scan_file(p)
                if v:
                    rel = p.relative_to(REPO_ROOT).as_posix()
                    for lnum, sname, snip in v:
                        print(f"🚨 [FILE VIOLATION] {rel}:{lnum} - {sname} -> {snip}")
                        violations_found += 1

    print("=" * 70)
    if violations_found > 0:
        print(f"❌ FAILED: {violations_found} secret violation(s) detected! Commit blocked.")
        sys.exit(1)
    else:
        print("✅ SUCCESS: Zero secrets or sensitive credentials detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
