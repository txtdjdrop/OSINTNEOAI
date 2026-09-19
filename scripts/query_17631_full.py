import requests
import json
import os

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach\searches"
BASE = "https://services2.arcgis.com/KaS5yngHhCOBHXdC/ArcGIS/rest/services"

def wgs84_to_mercator(lon, lat):
    import math
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return x, y

lon, lat = -117.988140256139, 33.706442743403
x, y = wgs84_to_mercator(lon, lat)

# 1. Get the specific parcel at 17631 Cameron
print("=== Parcel at 17631 Cameron ===")
parcels_url = f"{BASE}/Parcels/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "distance": 50,
    "units": "esriSRUnit_Meter",
    "outFields": "*",
    "f": "json",
    "returnGeometry": True
}
resp = requests.get(parcels_url, params=params, timeout=30)
parcels = resp.json()
features = parcels.get("features", [])
print(f"Parcels within 50m: {len(features)}")
for feat in features:
    attrs = feat["attributes"]
    print(f"  APN: {attrs.get('APN')} | Acres: {attrs.get('Acres')} | Area: {attrs.get('Shape__Area')}")

# 2. Get all streets with full details
print("\n=== Streets near 17631 Cameron (full details) ===")
streets_url = f"{BASE}/Centerlines_with_address_ranges/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "distance": 300,
    "units": "esriSRUnit_Meter",
    "outFields": "*",
    "f": "json",
    "returnGeometry": True
}
resp = requests.get(streets_url, params=params, timeout=30)
streets = resp.json()
features = streets.get("features", [])
print(f"Streets within 300m: {len(features)}")
for feat in features:
    attrs = feat["attributes"]
    name = f"{attrs.get('StPrefix', '')} {attrs.get('StNm', '')} {attrs.get('StSuffix', '')}".strip()
    print(f"  {name} | Speed: {attrs.get('SpeedLimit')} | Class: {attrs.get('OCTAClass')} | Addresses: {attrs.get('LeftMin')}-{attrs.get('LeftMax')} / {attrs.get('RightMin')}-{attrs.get('RightMax')}")

# 3. Query all zoning in HB to find SP14 details
print("\n=== Zoning SP14 details ===")
zoning_url = f"{BASE}/Zoning/FeatureServer/0/query"
params = {
    "where": "Base='SP14'",
    "outFields": "*",
    "f": "json",
    "returnGeometry": False
}
resp = requests.get(zoning_url, params=params, timeout=30)
zoning = resp.json()
features = zoning.get("features", [])
print(f"SP14 zones: {len(features)}")
for feat in features[:5]:
    print(f"  {feat['attributes']}")

# 4. Query FEMA flood zones
print("\n=== FEMA Flood Zones near 17631 Cameron ===")
flood_url = f"{BASE}/FEMA_Flood_Zones_Dec_2020/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "f": "json",
    "returnGeometry": False
}
resp = requests.get(flood_url, params=params, timeout=30)
flood = resp.json()
features = flood.get("features", [])
print(f"Flood zones: {len(features)}")
for feat in features[:3]:
    print(f"  {feat['attributes']}")

# 5. Query fault zones
print("\n=== Fault Zones near 17631 Cameron ===")
fault_url = f"{BASE}/Fault_Zones/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "f": "json",
    "returnGeometry": False
}
resp = requests.get(fault_url, params=params, timeout=30)
fault = resp.json()
features = fault.get("features", [])
print(f"Fault zones: {len(features)}")
for feat in features[:3]:
    print(f"  {feat['attributes']}")

# 6. Query oil wells
print("\n=== Oil Wells near 17631 Cameron ===")
oil_url = f"{BASE}/Oil/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "distance": 1000,
    "units": "esriSRUnit_Meter",
    "outFields": "*",
    "f": "json",
    "returnGeometry": False
}
resp = requests.get(oil_url, params=params, timeout=30)
oil = resp.json()
features = oil.get("features", [])
print(f"Oil wells within 1km: {len(features)}")
for feat in features[:5]:
    print(f"  {feat['attributes']}")

# 7. Query CIP Public Works projects
print("\n=== CIP Projects near 17631 Cameron ===")
cip_url = f"{BASE}/CIP-Public_Works/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "distance": 1000,
    "units": "esriSRUnit_Meter",
    "outFields": "*",
    "f": "json",
    "returnGeometry": False
}
resp = requests.get(cip_url, params=params, timeout=30)
cip = resp.json()
features = cip.get("features", [])
print(f"CIP projects within 1km: {len(features)}")
for feat in features[:5]:
    print(f"  {feat['attributes']}")

# 8. Query Soils
print("\n=== Soils near 17631 Cameron ===")
soil_url = f"{BASE}/Soils/FeatureServer/0/query"
params = {
    "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 102100}}),
    "geometryType": "esriGeometryPoint",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "f": "json",
    "returnGeometry": False
}
resp = requests.get(soil_url, params=params, timeout=30)
soil = resp.json()
features = soil.get("features", [])
print(f"Soil types: {len(features)}")
for feat in features[:3]:
    print(f"  {feat['attributes']}")

# Save everything
results = {
    "location": {"lon": lon, "lat": lat, "address": "17631 Cameron Ln, Huntington Beach, CA 92647"},
    "parcels": parcels.get("features", []),
    "streets": streets.get("features", []),
    "zoning_sp14": zoning.get("features", []),
    "flood_zones": flood.get("features", []),
    "fault_zones": fault.get("features", []),
    "oil_wells": oil.get("features", []),
    "cip_projects": cip.get("features", []),
    "soils": soil.get("features", [])
}
with open(os.path.join(OUTPUT_DIR, "17631_cameron_full_profile.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("\n=== DONE ===")
