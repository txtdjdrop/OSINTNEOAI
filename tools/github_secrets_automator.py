import os
import subprocess

def run_cmd(cmd):
    # Mask token
    safe_cmd = cmd
    if "ghp_" in cmd:
        safe_cmd = "echo [MASKED_TOKEN] | gh auth login --with-token"
    print(f"  [>] {safe_cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"  [!] Failed: {e.stderr.strip()}")

def configure_github_secrets():
    print("\n[+] Initializing Autonomous GitHub Actions Secrets Injection (Brainmedus-Arch)...")
    
    repo = "brainmedus-arch/OsintNeoAi"
    
    # We retrieve the token dynamically to avoid hardcoding it in the script file
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        pat, _ = winreg.QueryValueEx(key, "GITHUB_TOKEN_BRAINMEDUS")
    except:
        pat = os.environ.get("GITHUB_TOKEN_BRAINMEDUS")
        
    if not pat:
        print("  [!] Error: GITHUB_TOKEN_BRAINMEDUS not found in environment.")
        return
    
    # 1. Login to GitHub CLI using the PAT
    print("  [-] Authenticating GitHub CLI...")
    auth_cmd = f"echo {pat} | gh auth login --with-token"
    run_cmd(auth_cmd)
    
    # 2. Set Secrets
    secrets = {
        "SMTP_USER": "osintneoai@gmail.com",
        "SMTP_PASSWORD": "dbaptkyadvratiow",
        "ALERT_RECIPIENT_EMAIL": "amd949609@gmail.com",
        "GEMINI_API_KEY": "AIzaSyBVfyLZtm7F8eszpHHlyIRrGf_gBXmtCII"  # Extracted from GCP Console
    }
    
    for key, value in secrets.items():
        print(f"  [-] Injecting secret: {key}")
        cmd = f'echo {value} | gh secret set {key} -R {repo}'
        run_cmd(cmd)
        
    print(f"\n[✓] Successfully provisioned all GitHub Action Secrets for {repo}.")

if __name__ == "__main__":
    configure_github_secrets()
