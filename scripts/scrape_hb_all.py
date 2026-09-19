import requests
import json
import os

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE = "https://services2.arcgis.com/KaS5yngHhCOBHXdC/ArcGIS/rest/services"

def download(name, service_name, layer=0, where="1=1", fields="*", max_recs=50000):
    url = f"{BASE}/{service_name}/FeatureServer/{layer}/query"
    print(f"\n--- {name} ---")
    all_features = []
    offset = 0
    while offset < max_recs:
        params = {
            "where": where,
            "outFields": fields,
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
            print(f"  Fetched: {len(all_features)}", end="\r")
            if not data.get("exceededTransferLimit", False):
                break
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    outfile = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump({"count": len(all_features), "features": all_features}, f, indent=2)
    print(f"  Total: {len(all_features)}")
    return len(all_features)

total = 0

# Core datasets
total += download("HB_Parcels", "Parcels")
total += download("HB_Tracts", "Tracts")
total += download("HB_Zoning", "Zoning")
total += download("HB_Subsidence", "Subsidence")
total += download("HB_Street_Centers", "Centerlines_with_address_ranges")
total += download("HB_Vacant_Parcels", "Vacant_Parcels")
total += download("HB_Code_Complaints", "Code_Complaints")
total += download("HB_Oil", "Oil")
total += download("HB_Buildings", "Buildings")

# Projects & Development
total += download("HB_CIP_Public_Works", "CIP-Public_Works")
total += download("HB_DevServPts", "DevServPts")
total += download("HB_DevServPoly", "DevServPoly")
total += download("HB_Major_Projects_Points", "Completed_Points_Major_Projects")
total += download("HB_Major_Projects_Poly", "PlanCheck_Polygons_Major_Projects")
total += download("HB_UnderConstruction_Pts", "UnderConstruction_Point_Major_Projects")
total += download("HB_UnderConstruction_Poly", "UnderConstruction_Polygons_Major_Projects")

# Infrastructure
total += download("HB_PMP_2026", "HB_PMP_2026")
total += download("HB_Contour", "Contours2012")
total += download("HB_Soils", "Soils")
total += download("HB_FEMA_Flood", "FEMA_Flood_Zones_Dec_2020")
total += download("HB_Fault_Zones", "Fault_Zones")

# Telecom (underground network)
total += download("HB_Wilcon_Network", "Wilcon_Network_LN")
total += download("HB_ZAYO_Line", "ZAYO_US_Network_Line")
total += download("HB_ZAYO_Point", "ZAYO_US_Network_Point")

print(f"\n{'='*60}")
print(f"DONE - Total: {total}")
