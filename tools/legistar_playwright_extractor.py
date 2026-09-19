import os
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def scrape_legistar_playwright():
    print("\n[+] Initializing Headless Playwright Legistar Contract Extractor...")
    
    evidence_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/hb_records")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    targets = ["20-1432", "20-1799"]
    all_pdfs = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        for target in targets:
            print(f"\n  [-] Hunting for Contract {target} via headless browser...")
            try:
                page.goto("https://huntingtonbeach.legistar.com/Legislation.aspx", timeout=60000)
                page.wait_for_load_state("networkidle")
                
                # Fill the search box
                page.fill("input[id$='txtSearch']", target)
                
                # Click the specific Search button found in the DOM
                page.click("button#visibleSearchButton")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(4000)
                
                # Extract the results DOM to find the Detail link
                results_html = page.content()
                
                import re
                detail_links = re.findall(r'href=[\'"](LegislationDetail\.aspx\?[^\'"]+)[\'"]', results_html)
                detail_links = list(set(detail_links))
                
                if not detail_links:
                    print(f"  [!] No detail links found for {target} in the search results.")
                    page.screenshot(path=str(evidence_dir / f"legistar_error_{target}.png"))
                    continue
                    
                print(f"  [-] Found {len(detail_links)} detail links. Navigating to the first one...")
                
                # Navigate to the detail page
                detail_url = "https://huntingtonbeach.legistar.com/" + detail_links[0].replace("&amp;", "&")
                page.goto(detail_url, timeout=60000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(4000)
                
                # Extract all PDF attachment links from the detail page
                detail_html = page.content()
                attachments = re.findall(r'href=[\'"]([^\'"]*(?i:View\.ashx|Attachment|pdf)[^\'"]*)[\'"]', detail_html)
                
                pdf_urls = []
                for att in attachments:
                    if att.startswith('http'):
                        pdf_urls.append(att)
                    else:
                        pdf_urls.append("https://huntingtonbeach.legistar.com/" + att.lstrip('/'))
                        
                pdf_urls = list(set(pdf_urls))
                all_pdfs[target] = pdf_urls
                
                print(f"  [+] Extracted {len(pdf_urls)} unique PDF attachments for {target}")
                
            except Exception as e:
                print(f"  [!] Failed to extract {target}: {e}")

        browser.close()
        
    out_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/legistar_final_pdfs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_pdfs, f, indent=2)
        
    print(f"\n[✓] Deep Extraction Complete. Saved to {out_path}")
    for t, urls in all_pdfs.items():
        print(f"\n  [{t}] Attachments:")
        for u in urls:
            print(f"    -> {u}")

if __name__ == "__main__":
    scrape_legistar_playwright()
