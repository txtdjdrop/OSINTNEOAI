#!/usr/bin/env python3
"""Batch breach check using LeakCheck free public API."""
import requests
import time
import json
import os
from datetime import datetime, timezone

EMAILS = [
    # TTS Engineering (19)
    "tim@ttsengineering.net", "thomas@ttsengineering.net", "travis@ttsengineering.net",
    "jason@ttsengineering.net", "alex@ttsengineering.net", "kelly@ttsengineering.net",
    "julie@ttsengineering.net", "michael@ttsengineering.net", "jesus@ttsengineering.net",
    "brad@ttsengineering.net", "kalen@ttsengineering.net", "christian@ttsengineering.net",
    "jose@ttsengineering.net", "joe@ttsengineering.net", "htun@ttsengineering.net",
    "gregory@ttsengineering.net", "alden@ttsengineering.net", "casey@ttsengineering.net",
    "info@ttsengineering.net",
    # RPM Team (12)
    "richard@rpm-team.com", "david@rpm-team.com", "benjamin@rpm-team.com",
    "william@rpm-team.com", "vince@rpm-team.com", "paul@rpm-team.com",
    "ilfat@rpm-team.com", "baasandorj@rpm-team.com", "marcellus@rpm-team.com",
    "rick@rpm-team.com", "khayien@rpm-team.com", "contact@rpm-team.com",
    # EEC Environmental (8)
    "paul@eecenvironmental.com", "mark@eecenvironmental.com", "david@eecenvironmental.com",
    "mohdamin@eecenvironmental.com", "vinay@eecenvironmental.com", "tim@eecenvironmental.com",
    "jobs@eecenvironmental.com", "info@eecenvironmental.com",
    # HBPD (9)
    "hbpdinfo@hbpd.org", "traffic@hbpd.org", "press@hbpd.org",
    "crimetips@hbpd.org", "psu@hbpd.org", "cliaison@hbpd.org",
    "eric.parra@hbpd.org", "ryan.reilly@hbpd.org", "gabriel.ricci@hbpd.org",
    # City of HB (5)
    "julie.toledo@surfcity-hb.org", "HBCares@surfcity-hb.org",
    "phtf-casemanagers@surfcity-hb.org", "steven.folkes@surfcity-hb.org",
    "joseph-pinel@surfcity-hb.org",
]

API_URL = "https://leakcheck.io/api/public?check={email}"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "huntington_beach", "breach_check_results.json")

results = {"timestamp": datetime.now(timezone.utc).isoformat(), "total": len(EMAILS), "compromised": 0, "safe": 0, "errors": 0, "emails": {}}

for i, email in enumerate(EMAILS):
    print(f"[{i+1}/{len(EMAILS)}] Checking {email}...", end=" ", flush=True)
    try:
        resp = requests.get(API_URL.format(email=email), timeout=10)
        data = resp.json()
        if data.get("success") and data.get("found", 0) > 0:
            results["compromised"] += 1
            results["emails"][email] = {"status": "COMPROMISED", "found": data["found"], "sources": data.get("sources", [])}
            print(f"COMPROMISED ({data['found']} breaches)")
        elif data.get("success"):
            results["safe"] += 1
            results["emails"][email] = {"status": "SAFE", "found": 0}
            print("SAFE")
        else:
            results["errors"] += 1
            results["emails"][email] = {"status": "ERROR", "detail": data.get("error", "unknown")}
            print(f"ERROR: {data.get('error', 'unknown')}")
    except Exception as e:
        results["errors"] += 1
        results["emails"][email] = {"status": "ERROR", "detail": str(e)}
        print(f"ERROR: {e}")
    time.sleep(1.1)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*60}")
print(f"RESULTS: {results['compromised']} compromised / {results['safe']} safe / {results['errors']} errors")
print(f"{'='*60}")
for email, info in results["emails"].items():
    if info["status"] == "COMPROMISED":
        print(f"  [!] {email} - {info['found']} breaches")
        for src in info.get("sources", []):
            print(f"      - {src.get('name', '?')} ({src.get('date', '?')})")
print(f"\nResults saved to: {OUTPUT}")
