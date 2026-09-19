import requests
import json
import os
import math

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach\searches"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE = "https://services2.arcgis.com/KaS5yngHhCOBHXdC/ArcGIS/rest/services"

# Convert WGS84 to Web Mercator
def wgs84_to_mercator(lon, lat):
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return x, y

# 17631 Cameron Lane coordinates (WGS84)
lon, lat = -117.988140256139, 33.706442743403
x, y = wgs84_to_mercator(lon, lat)
print(f"Web Mercator: {x}, {y}")

# 1. Query parcels near this location
print("\n=== Querying parcels near 17631 Cameron ===")
parcels_url = f"{BASE}/Parcels/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
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

# 2. Query tracts
print("\n=== Querying tracts ===")
tracts_url = f"{BASE}/Tracts/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
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
    print(f"  Tract fields: {list(attrs.keys())[:10]}")
    print(f"  Values: {attrs}")

# 3. Query streets
print("\n=== Querying streets ===")
streets_url = f"{BASE}/Centerlines_with_address_ranges/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
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
    print(f"  {attrs.get('STREETNAME', attrs.get('FULLNAME', 'N/A'))} | {attrs}")

# 4. Query zoning
print("\n=== Querying zoning ===")
zoning_url = f"{BASE}/Zoning/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
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

# 5. Query subsidence
print("\n=== Querying subsidence ===")
sub_url = f"{BASE}/Subsidence/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
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
    "location": {"lon": lon, "lat": lat, "mercator_x": x, "mercator_y": y},
    "parcels_nearby": parcels.get("features", []),
    "tracts": tracts.get("features", []),
    "streets_nearby": streets.get("features", []),
    "zoning": zoning.get("features", []),
    "subsidence": sub.get("features", [])
}
with open(os.path.join(OUTPUT_DIR, "17631_cameron_spatial_query.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("\n=== DONE ===")
