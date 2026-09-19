import requests
import json
import os
from datetime import datetime

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights\infrastructure"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download(name, url, max_recs=50000):
    print(f"\n=== {name} ===")
    all_feats = []
    offset = 0
    batch = 1000
    while offset < max_recs:
        params = {"where": "1=1", "outFields": "*", "resultOffset": offset, "resultRecordCount": batch, "f": "json", "returnGeometry": "true"}
        try:
            resp = requests.get(url, params=params, timeout=60)
            data = resp.json()
            feats = data.get("features", [])
            if not feats:
                break
            all_feats.extend(feats)
            offset += len(feats)
            print(f"  {len(all_feats)}...")
            if not data.get("exceededTransferLimit", False):
                break
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    outfile = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump({"name": name, "count": len(all_feats), "time": datetime.now().isoformat(), "features": all_feats}, f, indent=2)
    print(f"  SAVED: {len(all_feats)} records")
    return len(all_feats)

layers = [
    # Storm Drain / Creek Studies
    ("SD_Creek_Scour_Study", "https://www.ocgis.com/survey/rest/services/WebApps/SD_Creek_Scour_Study_Publish/MapServer/0/query"),
    ("SD_Creek_Scour_Status", "https://www.ocgis.com/survey/rest/services/WebApps/SD_Creek_Scour_Study_Status_Publish/FeatureServer/0/query"),
    
    # Street Centerlines (Eaton, Shea, SL, etc.)
    ("Street_Centerlines", "https://www.ocgis.com/survey/rest/services/WebApps/Street_Centerlines/FeatureServer/0/query"),
    ("Road_Index_Centerlines", "https://www.ocgis.com/survey/rest/services/WebApps/Road_Index_Centerlines/FeatureServer/0/query"),
    
    # Transportation / Right of Way
    ("Transportation_Features", "https://www.ocgis.com/survey/rest/services/WebApps/TransportationFeatures/FeatureServer/0/query"),
    ("Right_of_Way", "https://www.ocgis.com/survey/rest/services/WebApps/RightofWay/FeatureServer/0/query"),
    
    # Survey Documents / Maps
    ("Survey_Documents", "https://www.ocgis.com/survey/rest/services/WebApps/SurveyDocuments/FeatureServer/0/query"),
    ("Parcel_Features", "https://www.ocgis.com/survey/rest/services/WebApps/ParcelFeatures/FeatureServer/0/query"),
    
    # County Owned Property Utilities
    ("County_Property_Utilities", "https://www.ocgis.com/survey/rest/services/CountyOwnedPropertyUtilities/CountyOwnedPropertyUtilitiesRematch/FeatureServer/0/query"),
    
    # Field Services
    ("Field_Services_CL_RW", "https://www.ocgis.com/survey/rest/services/FieldServices/Field_Services_CL_RW/FeatureServer/0/query"),
    ("City_Ties", "https://www.ocgis.com/survey/rest/services/FieldServices/City_Ties/FeatureServer/0/query"),
    
    # Tentative Maps
    ("Tentative_Maps_Web", "https://www.ocgis.com/survey/rest/services/WebApps/TentativeMaps/FeatureServer/0/query"),
]

total = 0
for name, url in layers:
    total += download(name, url)

print(f"\n{'='*60}")
print(f"COMPLETE - Total: {total} infrastructure records")
