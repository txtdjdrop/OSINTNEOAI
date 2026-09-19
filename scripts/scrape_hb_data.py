import requests
import json
import os

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def query(url, where="1=1", out_fields="*", max_recs=5000, label="data"):
    print(f"\n--- {label} ---")
    all_features = []
    offset = 0
    while offset < max_recs:
        params = {
            "where": where,
            "outFields": out_fields,
            "resultOffset": offset,
            "resultRecordCount": 1000,
            "f": "json",
            "returnGeometry": "true"
        }
        try:
            resp = requests.get(url, params=params, timeout=60)
            data = resp.json()
            features = data.get("features", [])
            if not features:
                break
            all_features.extend(features)
            offset += len(features)
            if not data.get("exceededTransferLimit", False):
                break
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    outfile = os.path.join(OUTPUT_DIR, f"{label}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump({"count": len(all_features), "features": all_features}, f, indent=2)
    print(f"  Records: {len(all_features)}")
    return len(all_features)

# 1. Tracts - search for 405 tract or near Slater/Cameron area
tracts_url = "https://services2.arcgis.com/KaS5yngHhCOBHXdC/arcgis/rest/services/Tracts/FeatureServer/0/query"
query(tracts_url, "1=1", "*", 5000, "HB_Tracts")

# 2. Subsidence
sub_url = "https://services2.arcgis.com/KaS5yngHhCOBHXdC/arcgis/rest/services/Subsidence/FeatureServer/0/query"
query(sub_url, "1=1", "*", 5000, "HB_Subsidence")

# 3. Try to find Huntington Beach parcels via ArcGIS Hub datasets
# Search for parcel feature service
parcels_search = "https://hub.arcgis.com/api/v3/datasets?q=huntington+beach+parcels&filter[orgId]=KaS5yngHhCOBHXdC&fields[datasets]=name,url,slug&page[size]=5"
resp = requests.get(parcels_search, timeout=30)
parcels_data = resp.json()
print("\n=== Parcel datasets found ===")
for d in parcels_data.get("data", []):
    attrs = d.get("attributes", {})
    print(f"  {attrs.get('name')}: {attrs.get('url', 'N/A')}")

# 4. Search for storm drain / underground utility datasets
storm_search = "https://hub.arcgis.com/api/v3/datasets?q=huntington+beach+storm+drain+pipe&filter[orgId]=KaS5yngHhCOBHXdC&fields[datasets]=name,url,slug&page[size]=10"
resp = requests.get(storm_search, timeout=30)
storm_data = resp.json()
print("\n=== Storm drain datasets ===")
for d in storm_data.get("data", []):
    attrs = d.get("attributes", {})
    print(f"  {attrs.get('name')}: {attrs.get('url', 'N/A')}")

# 5. Search for transformer / electrical / underground
elec_search = "https://hub.arcgis.com/api/v3/datasets?q=huntington+beach+transformer+electrical+underground&filter[orgId]=KaS5yngHhCOBHXdC&fields[datasets]=name,url,slug&page[size]=10"
resp = requests.get(elec_search, timeout=30)
elec_data = resp.json()
print("\n=== Electrical/Underground datasets ===")
for d in elec_data.get("data", []):
    attrs = d.get("attributes", {})
    print(f"  {attrs.get('name')}: {attrs.get('url', 'N/A')}")
