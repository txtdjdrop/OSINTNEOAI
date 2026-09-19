import requests
import json
import os

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach\searches"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE = "https://services2.arcgis.com/KaS5yngHhCOBHXdC/ArcGIS/rest/services"

# 1. Query parcels with address search via geocoding
# 17631 Cameron Lane, Huntington Beach, CA
print("=== Geocoding 17631 Cameron Lane, Huntington Beach ===")
geocode_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
params = {
    "SingleLine": "17631 Cameron Lane, Huntington Beach, CA",
    "f": "json",
    "outFields": "*",
    "maxLocations": 5
}
resp = requests.get(geocode_url, params=params, timeout=30)
geocode = resp.json()
candidates = geocode.get("candidates", [])
print(f"Found {len(candidates)} candidates")
for c in candidates:
    print(f"  {c.get('address')} | Score: {c.get('score')} | Location: {c.get('location')}")

if candidates:
    loc = candidates[0]["location"]
    print(f"\nUsing location: {loc}")
    
    # 2. Query parcels near this location
    print("\n=== Querying parcels near 17631 Cameron ===")
    parcels_url = f"{BASE}/Parcels/FeatureServer/0/query"
    params = {
        "geometry": json.dumps({"x": loc["x"], "y": loc["y"], "spatialReference": {"wkid": 102100}}),
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": 200,
        "units": "esriSRUnit_Meter",
        "outFields": "*",
        "f": "json",
        "returnGeometry": True
    }
    resp = requests.get(parcels_url, params=params, timeout=30)
    parcels = resp.json()
    features = parcels.get("features", [])
    print(f"Parcels within 200m: {len(features)}")
    for feat in features[:5]:
        attrs = feat["attributes"]
        print(f"  APN: {attrs.get('APN')} | Area: {attrs.get('Shape__Area')}")

# 3. Query tracts near this location
print("\n=== Querying tracts near 17631 Cameron ===")
tracts_url = f"{BASE}/Tracts/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": loc["x"], "y": loc["y"], "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "f": "json",
    "returnGeometry": True
}
resp = requests.get(tracts_url, params=params, timeout=30)
tracts = resp.json()
features = tracts.get("features", [])
print(f"Tracts containing point: {len(features)}")
for feat in features[:3]:
    attrs = feat["attributes"]
    print(f"  Tract: {attrs}")

# 4. Query streets near this location
print("\n=== Querying streets near 17631 Cameron ===")
streets_url = f"{BASE}/Centerlines_with_address_ranges/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": loc["x"], "y": loc["y"], "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "distance": 500,
    "units": "esriSRUnit_Meter",
    "outFields": "*",
    "f": "json",
    "returnGeometry": True
}
resp = requests.get(streets_url, params=params, timeout=30)
streets = resp.json()
features = streets.get("features", [])
print(f"Streets within 500m: {len(features)}")
for feat in features[:5]:
    attrs = feat["attributes"]
    print(f"  {attrs.get('STREETNAME', attrs.get('FULLNAME', 'N/A'))}")

# 5. Query zoning
print("\n=== Querying zoning near 17631 Cameron ===")
zoning_url = f"{BASE}/Zoning/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": loc["x"], "y": loc["y"], "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "f": "json",
    "returnGeometry": True
}
resp = requests.get(zoning_url, params=params, timeout=30)
zoning = resp.json()
features = zoning.get("features", [])
print(f"Zoning polygons: {len(features)}")
for feat in features[:3]:
    attrs = feat["attributes"]
    print(f"  {attrs}")

# 6. Query subsidence
print("\n=== Querying subsidence near 17631 Cameron ===")
sub_url = f"{BASE}/Subsidence/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": loc["x"], "y": loc["y"], "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "f": "json",
    "returnGeometry": True
}
resp = requests.get(sub_url, params=params, timeout=30)
sub = resp.json()
features = sub.get("features", [])
print(f"Subsidence zones: {len(features)}")
for feat in features[:3]:
    attrs = feat["attributes"]
    print(f"  {attrs}")

# Save all results
results = {
    "geocode": geocode,
    "parcels_nearby": parcels.get("features", []),
    "tracts": tracts.get("features", []),
    "streets_nearby": streets.get("features", []),
    "zoning": zoning.get("features", []),
    "subsidence": sub.get("features", [])
}
with open(os.path.join(OUTPUT_DIR, "17631_cameron_spatial_query.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("\n=== DONE ===")
