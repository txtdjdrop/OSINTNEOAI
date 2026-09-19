import requests
import json
import os
from datetime import datetime

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights\street_searches"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def search(name, url, where, fields="*", max_recs=5000):
    print(f"\n=== {name} ===")
    all_feats = []
    offset = 0
    while offset < max_recs:
        params = {"where": where, "outFields": fields, "resultOffset": offset, "resultRecordCount": 1000, "f": "json", "returnGeometry": "true"}
        try:
            resp = requests.get(url, params=params, timeout=60)
            data = resp.json()
            feats = data.get("features", [])
            if not feats:
                break
            all_feats.extend(feats)
            offset += len(feats)
            if not data.get("exceededTransferLimit", False):
                break
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    outfile = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump({"name": name, "where": where, "count": len(all_feats), "features": all_feats}, f, indent=2)
    print(f"  FOUND: {len(all_feats)} records")
    return len(all_feats)

street_url = "https://www.ocgis.com/survey/rest/services/WebApps/Street_Centerlines/FeatureServer/0/query"
tent_url = "https://www.ocgis.com/survey/rest/services/Landbase/TentativeMaps/FeatureServer/10/query"

total = 0

# Search for specific streets
for s in ["EATON", "SHEA", "SOUTH LAKE", "STORM", "HBNC", "UNDERGROUND"]:
    w = f"UPPER(STREETNAME) LIKE '%{s}%'"
    total += search(f"Street_{s.replace(' ','_')}", street_url, w)

# Sample some street data to see what's there
total += search("Street_Sample", street_url, "1=1", fields="STREETNAME,OLDSTREETNAME,PREFIX,SUFFIX,STREETCODE,NOTES", max_recs=100)

print(f"\n{'='*60}")
print(f"DONE - Total: {total}")
