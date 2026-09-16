import os
import subprocess
import json
from pathlib import Path

def run_cmd(cmd):
    print(f"  [>] {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"  [!] Command Failed: {e.stderr.strip() if e.stderr else 'Unknown Error'}")
        return None

def automate_gcp_setup():
    print("[+] Beginning Autonomous GCP IAM & VPS Setup...")
    project_id = "project-837e5009-a8eb-4b14-a12"
    sa_email = "x22service-107379942474@gcp-sa-datamigration.iam.gserviceaccount.com"
    
    print(f"[-] Target Project: {project_id}")
    print(f"[-] Target Service Account: {sa_email}")
    
    # Adding --quiet to prevent hanging on user prompts
    run_cmd(f"gcloud services enable compute.googleapis.com iam.googleapis.com cloudresourcemanager.googleapis.com --project={project_id} --quiet")
    
    key_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/keys/gcp_sa_key.json"
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    
    print("[-] Generating new JSON key for Service Account...")
    run_cmd(f"gcloud iam service-accounts keys create {key_path} --iam-account={sa_email} --project={project_id} --quiet")
    
    vps_name = "osint-neo-vps-1"
    print(f"[-] Provisioning Compute Engine VPS: {vps_name}...")
    run_cmd(f"gcloud compute instances create {vps_name} --project={project_id} --zone=us-central1-a --machine-type=e2-micro --image-family=debian-12 --image-project=debian-cloud --service-account={sa_email} --scopes=https://www.googleapis.com/auth/cloud-platform --quiet")
    
    print("\n[✓] Autonomous GCP setup complete.")

if __name__ == "__main__":
    automate_gcp_setup()
