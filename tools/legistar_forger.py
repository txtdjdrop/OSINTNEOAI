import os
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from pathlib import Path

def forge_legistar_post():
    print("\n[+] Initializing ASP.NET ViewState Forgery for HB Legistar...")
    
    dom_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/hb_records/legistar_dom.html")
    if not dom_path.exists():
        print(f"  [!] Missing DOM payload: {dom_path}")
        return
        
    html = dom_path.read_text(encoding='utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract ASP.NET Hidden Fields
    viewstate = soup.find('input', id='__VIEWSTATE')
    viewstategen = soup.find('input', id='__VIEWSTATEGENERATOR')
    eventvalidation = soup.find('input', id='__EVENTVALIDATION')
    
    if not viewstate:
        print("  [!] Failed to extract __VIEWSTATE. The target may have rotated security tokens.")
        return
        
    print(f"  [+] Captured __VIEWSTATE token ({len(viewstate['value'])} chars)")
    
    # We are forging a POST request to search for File 20-1432 and 20-1799
    # Legistar uses a highly specific payload structure
    url = "https://huntingtonbeach.legistar.com/Legislation.aspx"
    
    # Common headers to bypass basic WAF
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': url,
        'Origin': 'https://huntingtonbeach.legistar.com'
    }
    
    targets = ["20-1432", "20-1799"]
    
    out_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/hb_records")
    
    for target in targets:
        print(f"\n  [-] Forging POST payload for File {target}...")
        
        # The form data structure for Legistar search
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate['value'],
            '__VIEWSTATEGENERATOR': viewstategen['value'] if viewstategen else '',
            '__EVENTVALIDATION': eventvalidation['value'] if eventvalidation else '',
            'ctl00$ContentPlaceHolder1$txtSearch': target,
            'ctl00$ContentPlaceHolder1$btnSearch': 'Search Legislation'
        }
        
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=encoded_data, headers=headers)
            with urllib.request.urlopen(req) as response:
                result_html = response.read().decode('utf-8')
                
            out_file = out_dir / f"legistar_result_{target}.html"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(result_html)
                
            print(f"  [+] Server accepted forged POST. Results dumped to {out_file.name}")
            
            # Immediately parse the result for PDF links
            pdf_links = re.findall(r'href=[\'"]([^\'"]*(?i:View\.ashx|Attachment|pdf)[^\'"]*)[\'"]', result_html)
            
            absolute_links = []
            for link in pdf_links:
                if link.startswith('http'):
                    absolute_links.append(link)
                else:
                    absolute_links.append(f"https://huntingtonbeach.legistar.com/{link.lstrip('/')}")
                    
            if absolute_links:
                print(f"  [!] Found {len(set(absolute_links))} attached documents!")
                for link in list(set(absolute_links))[:3]:
                    print(f"      -> {link}")
            else:
                print("  [-] No PDF attachments found in the search result DOM.")
                
        except Exception as e:
            print(f"  [!] POST Request Failed for {target}: {e}")

    print("\n[✓] Legistar ViewState Forgery Complete.")

if __name__ == "__main__":
    forge_legistar_post()
