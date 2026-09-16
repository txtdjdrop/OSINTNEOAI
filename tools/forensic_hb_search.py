import os
import json
from pathlib import Path
from collections import defaultdict

# The newly ingested data from the swarm
TARGET_DATA_DIR = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/huntington_beach")
SEARCH_FILES = [
    TARGET_DATA_DIR / "HB_Buildings.json",
    TARGET_DATA_DIR / "HB_Oil.json",
    TARGET_DATA_DIR / "HB_Parcels.json",
    TARGET_DATA_DIR / "HB_Street_Centers.json",
    TARGET_DATA_DIR / "HB_Subsidence.json",
    TARGET_DATA_DIR / "HB_Tracts.json",
    TARGET_DATA_DIR / "HB_Zoning.json",
    TARGET_DATA_DIR / "searches/17631_cameron_spatial_query.json"
]

TARGETS = [
    "17631", "17642", "cameron", "beach blvd", "stormtech", "mercy", "hbnc", 
    "shea", "baker", "142-075", "142-261"
]

def forensic_search_new_data():
    print("[+] Searching newly acquired HB GIS and Swarm Data for target overlaps...")
    findings = defaultdict(list)
    files_scanned = 0
    
    for file_path in SEARCH_FILES:
        if not file_path.exists(): 
            print(f"  [-] Missing: {file_path.name}")
            continue
            
        files_scanned += 1
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to load as JSON for structured searching
                try:
                    data = json.load(f)
                    # Convert whole structure to string to search easily
                    content = json.dumps(data).lower()
                except:
                    # Fallback to plain text read
                    f.seek(0)
                    content = f.read().lower()

                if any(tk in content for tk in TARGETS):
                    # We have a hit in this file, let's extract snippets
                    lines = content.split('},') # Split by JSON object roughly
                    for obj in lines:
                        if any(tk in obj for tk in TARGETS):
                            findings[file_path.name].append(obj[:500] + "...")
        except Exception as e:
            print(f"  [!] Error reading {file_path.name}: {e}")

    print(f"\n[✓] Scanned {files_scanned} files.")
    
    if findings:
        out_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/huntington_beach/forensic_overlaps.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(findings, f, indent=2)
            
        print(f"[✓] Found contextual matches in {len(findings)} files.")
        for file, hits in findings.items():
            print(f"\n--- {file} ({len(hits)} hits) ---")
            for hit in hits[:3]:
                print(f"  > {hit[:150]}...")
        print(f"\n[✓] Full extraction dumped to {out_path}")
    else:
        print("[-] No specific targets found in the new HB datasets.")

if __name__ == "__main__":
    forensic_search_new_data()
