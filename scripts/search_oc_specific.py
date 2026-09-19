import requests
import json
import os
from datetime import datetime

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights\specific_searches"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def search_layer(name, url, where_clause, fields="*", max_recs=10000):
    print(f"\n=== {name} ===")
    print(f"  WHERE: {where_clause}")
    all_feats = []
    offset = 0
    batch = 1000
    while offset < max_recs:
        params = {"where": where_clause, "outFields": fields, "resultOffset": offset, "resultRecordCount": batch, "f": "json", "returnGeometry": "true"}
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
        json.dump({"name": name, "where": where_clause, "count": len(all_feats), "time": datetime.now().isoformat(), "features": all_feats}, f, indent=2)
    print(f"  FOUND: {len(all_feats)} records")
    return len(all_feats)

# Street name searches on Street_Centerlines
street_url = "https://www.ocgis.com/survey/rest/services/WebApps/Street_Centerlines/FeatureServer/0/query"

streets_to_search = ["EATON", "SHEA", "SL%20%", "STORMTECH", "HBNC", "UNDERGROUND", "220V"]

total = 0
for street in streets_to_search:
    where = f"UPPER(STREETNAME) LIKE '%{street.upper()}%' OR UPPER(STREET_NAM) LIKE '%{street.upper()}%' OR UPPER(FULLNAME) LIKE '%{street.upper()}%'"
    total += search_layer(f"Street_{street.replace('%','_').replace(' ','_')}", street_url, where)

# Also search TentativeMaps for these terms
tentative_url = "https://www.ocgis.com/survey/rest/services/Landbase/TentativeMaps/FeatureServer/10/query"
for term in ["EATON", "SHEA", "HBNC", "STORM"]:
    where = f"UPPER(CITY) LIKE '%{term}%' OR UPPER(ENGINEER) LIKE '%{term}%' OR UPPER(CompanyName) LIKE '%{term}%'"
    total += search_layer(f"Tentative_{term}", tentative_url, where)

# Search Geodetic for control points
geodetic_url = "https://www.ocgis.com/survey/rest/services/OCLandInsights/Geodetic/MapServer/999018/query"
where = "1=1"
total += search_layer("Horizontal_Control_Points", geodetic_url, where)

print(f"\n{'='*60}")
print(f"SEARCH COMPLETE - Total: {total} records found")
