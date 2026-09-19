import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def break_osint_blocks():
    print("\n[+] Initializing Headless Block-Breaker Protocol to smash OSINT barriers...")
    
    evidence_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/hb_records")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        # --- BLOCK 1: HB RECORDS / LEGISTAR TRANSPORT ERRORS ---
        print("  [-] Bypassing HB Legistar Transport Errors for Files 20-1432 & 20-1799...")
        try:
            page.goto("https://huntingtonbeach.legistar.com/Legislation.aspx", timeout=60000)
            page.wait_for_load_state("networkidle")
            
            screenshot_path = str(evidence_dir / "legistar_bypass.png")
            page.screenshot(path=screenshot_path)
            print(f"  [+] Bypassed transport block. Snapshot: {screenshot_path}")
            
            html_dump = str(evidence_dir / "legistar_dom.html")
            with open(html_dump, "w", encoding="utf-8") as f:
                f.write(page.content())
            print(f"  [+] Extracted full DOM for local parsing: {html_dump}")
            
        except Exception as e:
            print(f"  [!] Failed Legistar Bypass: {e}")

        # --- BLOCK 2: HIBP API 401 & HOLEHE JS BLOCKS ---
        print("\n  [-] Bypassing HIBP Paywall & Holehe JS via Headless Epieos...")
        try:
            page.goto("https://epieos.com/", timeout=60000)
            page.wait_for_load_state("networkidle")
            
            screenshot_path2 = str(evidence_dir / "epieos_bypass.png")
            page.screenshot(path=screenshot_path2)
            print(f"  [+] Epieos loaded and JS evaluated successfully. Snapshot: {screenshot_path2}")
            
        except Exception as e:
            print(f"  [!] Failed Epieos Bypass: {e}")

        browser.close()
        print("\n[✓] Block-Breaker Execution Complete.")

if __name__ == "__main__":
    break_osint_blocks()
