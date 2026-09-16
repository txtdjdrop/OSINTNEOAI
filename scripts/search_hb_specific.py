import json
import os
import requests

HB_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach"
SEARCH_DIR = os.path.join(HB_DIR, "searches")
os.makedirs(SEARCH_DIR, exist_ok=True)

# 1. Search parcels for 17631 Cameron and surrounding area
print("=== Searching HB Parcels ===")
parcels_file = os.path.join(HB_DIR, "HB_Parcels.json")
with open(parcels_file, "r", encoding="utf-8") as f:
    parcels_data = json.load(f)

print(f"Total parcels: {parcels_data['count']}")

# Search for specific addresses/streets
search_terms = ["17631", "CAMERON", "SLATER", "EATON", "SHEA", "NAVIGATION", "MERCY"]
results = {}
for feat in parcels_data["features"]:
    attrs = feat["attributes"]
    # Check all string fields for matches
    for key, val in attrs.items():
        if isinstance(val, str):
            val_upper = val.upper()
            for term in search_terms:
                if term in val_upper:
                    if term not in results:
                        results[term] = []
                    results[term].append(attrs)
                    break

for term, matches in results.items():
    print(f"\n'{term}': {len(matches)} matches")
    for m in matches[:3]:
        print(f"  {m.get('SITE_ADDR', 'N/A')} | {m.get('OWNER_NAME', 'N/A')} | APN: {m.get('APN', 'N/A')}")

with open(os.path.join(SEARCH_DIR, "parcel_search_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

# 2. Search street centers for specific streets
print("\n=== Searching HB Street Centers ===")
streets_file = os.path.join(HB_DIR, "HB_Street_Centers.json")
if os.path.exists(streets_file):
    with open(streets_file, "r", encoding="utf-8") as f:
        streets_data = json.load(f)
    
    print(f"Total streets: {streets_data['count']}")
    street_results = {}
    street_search = ["CAMERON", "SLATER", "EATON", "SHEA", "NAVIGATION"]
    for feat in streets_data["features"]:
        attrs = feat["attributes"]
        for key, val in attrs.items():
            if isinstance(val, str):
                val_upper = val.upper()
                for term in street_search:
                    if term in val_upper:
                        if term not in street_results:
                            street_results[term] = []
                        street_results[term].append(attrs)
                        break
    
    for term, matches in street_results.items():
        print(f"\n'{term}': {len(matches)} street segments")
        for m in matches[:2]:
            print(f"  {m.get('STREETNAME', m.get('FULLNAME', 'N/A'))} | {m.get('FROMADDR_L', '')}-{m.get('TOADDR_L', '')}")

    with open(os.path.join(SEARCH_DIR, "street_search_results.json"), "w", encoding="utf-8") as f:
        json.dump(street_results, f, indent=2, default=str)

# 3. Search DevServPts for underground/utility permits
print("\n=== Searching HB DevServPts (permits) ===")
dev_file = os.path.join(HB_DIR, "HB_DevServPts.json")
if os.path.exists(dev_file):
    with open(dev_file, "r", encoding="utf-8") as f:
        dev_data = json.load(f)
    
    print(f"Total dev points: {dev_data['count']}")
    # Check field names
    if dev_data["features"]:
        print(f"Fields: {list(dev_data['features'][0]['attributes'].keys())[:15]}")
    
    permit_results = {}
    permit_search = ["STORM", "UNDERGROUND", "TRANSFORMER", "ELECTRIC", "UTILITY", "WATER", "SEWER", "DRAIN"]
    for feat in dev_data["features"]:
        attrs = feat["attributes"]
        for key, val in attrs.items():
            if isinstance(val, str):
                val_upper = val.upper()
                for term in permit_search:
                    if term in val_upper:
                        if term not in permit_results:
                            permit_results[term] = []
                        permit_results[term].append(attrs)
                        break
    
    for term, matches in permit_results.items():
        print(f"\n'{term}': {len(matches)} permits")
    
    with open(os.path.join(SEARCH_DIR, "permit_search_results.json"), "w", encoding="utf-8") as f:
        json.dump(permit_results, f, indent=2, default=str)

print("\n=== DONE ===")
