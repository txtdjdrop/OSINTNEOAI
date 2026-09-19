import urllib.request
import re
import json
from pathlib import Path

def deep_extract():
    print("\n[+] Initializing Legistar Deep Extractor...")
    base_url = "https://huntingtonbeach.legistar.com/"
    results_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/hb_records")
    
    targets = ["20-1432", "20-1799"]
    all_pdfs = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for target in targets:
        res_file = results_dir / f"legistar_result_{target}.html"
        if not res_file.exists():
            print(f"  [!] Missing result file: {res_file.name}")
            continue
            
        html = res_file.read_text(encoding='utf-8', errors='ignore')
        
        detail_links = re.findall(r'href=[\'"](LegislationDetail\.aspx\?[^\'"]+)[\'"]', html)
        detail_links = list(set(detail_links))
        
        print(f"  [-] Found {len(detail_links)} detail links for {target}")
        
        pdf_urls = []
        for link in detail_links:
            full_url = base_url + link.replace("&amp;", "&")
            print(f"    [>] Fetching {full_url}")
            try:
                req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    detail_html = response.read().decode('utf-8')
                    
                attachments = re.findall(r'href=[\'"]([^\'"]*(?i:View\.ashx|Attachment|pdf)[^\'"]*)[\'"]', detail_html)
                for att in attachments:
                    if att.startswith('http'):
                        pdf_urls.append(att)
                    else:
                        pdf_urls.append(base_url + att.lstrip('/'))
            except Exception as e:
                print(f"    [!] Failed to fetch detail page: {e}")
                
        all_pdfs[target] = list(set(pdf_urls))
        print(f"  [+] Extracted {len(all_pdfs[target])} unique PDF attachments for {target}")

    out_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/legistar_final_pdfs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_pdfs, f, indent=2)
        
    print(f"\n[✓] Deep Extraction Complete. Saved to {out_path}")

if __name__ == "__main__":
    deep_extract()
