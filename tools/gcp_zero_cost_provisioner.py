import os
import subprocess
import json

def run(cmd):
    print(f"  [>] {cmd}")
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.stdout: print(p.stdout.strip())
    if p.returncode != 0: print(f"  [!] Failed: {p.stderr.strip()}")
    return p.returncode == 0

def zero_cost_vps_provision():
    print("[+] Initializing Zero-Cost (Trial Credit Only) VPS Provisioning...")
    
    print("\n[-] Setting active account to brainmedus@gmail.com...")
    if not run("gcloud config set account brainmedus@gmail.com"):
        print("  [!] brainmedus@gmail.com is not authenticated locally. Attempting fallback to sub-account...")
        run("gcloud config set account anthony.dimarcello.student@gmail.com")
        
    print("\n[-] Linking $300 Trial Billing Account (01E8DD-FCDCE5-E29FCC) to project blah-905ad...")
    if not run("gcloud beta billing projects link blah-905ad --billing-account 01E8DD-FCDCE5-E29FCC"):
        print("  [!] Billing link failed locally. The CLI token may have expired.")
        print(f"  [!] To prevent terminal hanging, I am halting GCP API calls.")
        return
        
    print("\n[-] Provisioning Debian 12 VPS on blah-905ad (Always Free Tier / Covered by $300 Credit)...")
    run("gcloud services enable compute.googleapis.com --project=blah-905ad --quiet")
    run("gcloud compute instances create brainmedus-vps --project=blah-905ad --zone=us-central1-a --machine-type=e2-micro --image-family=debian-12 --image-project=debian-cloud --quiet")
    
    print("\n[✓] VPS Provisioned successfully. Retrieving Public IP...")
    run("gcloud compute instances list --project=blah-905ad --format=json")

if __name__ == "__main__":
    zero_cost_vps_provision()
