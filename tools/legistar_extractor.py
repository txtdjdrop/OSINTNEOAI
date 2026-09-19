import os
import json
import re
from pathlib import Path

def extract_legistar_contracts():
    print("[+] Initializing Autonomous Legistar Contract Extractor...")
    
    dom_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/hb_records/legistar_dom.html")
    if not dom_path.exists():
        print(f"  [!] Missing DOM payload: {dom_path}")
        return
        
    print(f"  [-] Reading {dom_path.name}...")
    html = dom_path.read_text(encoding='utf-8', errors='ignore')
    
    print("\n  [-] Hunting for Contract 20-1432 & 20-1799 references...")
    
    hits = []
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if "20-1432" in line or "20-1799" in line:
            clean_line = re.sub(r'<[^>]+>', ' ', line).strip()
            if clean_line:
                hits.append(f"Line {i}: {clean_line}")
                
    pdf_links = re.findall(r'href=[\'"]([^\'"]*(?i:View\.ashx|Attachment|pdf)[^\'"]*)[\'"]', html)
    absolute_links = []
    for link in pdf_links:
        if link.startswith('http'):
            absolute_links.append(link)
        else:
            absolute_links.append(f"https://huntingtonbeach.legistar.com/{link.lstrip('/')}")
            
    absolute_links = list(set(absolute_links))

    res = {
        "target_file_hits": hits,
        "potential_pdf_urls": absolute_links
    }
    
    out_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/legistar_contract_urls.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        
    print(f"\n[✓] Extraction Complete.")
    print(f"  - Found {len(hits)} direct text references to the contract files.")
    print(f"  - Extracted {len(absolute_links)} potential PDF/Attachment URLs.")
    print(f"  - Dumped to {out_path}")
    
    print("\n  [+] Top 5 Extracted Document URLs:")
    for link in absolute_links[:5]:
        print(f"      {link}")

if __name__ == "__main__":
    extract_legistar_contracts()
