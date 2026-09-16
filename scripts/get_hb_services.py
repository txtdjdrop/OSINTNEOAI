import requests
import json
import os

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\huntington_beach"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_item_info(item_id):
    url = f"https://www.arcgis.com/sharing/content/items/{item_id}?f=json"
    resp = requests.get(url, timeout=30)
    return resp.json()

# Key HB items
items = {
    "Parcels": "26662ee736854849b387110da38efa6e",
    "Tracts": "82fb4783371940fd9d3d45f26eda0963",
    "Storm_Drain_Finder": "18b0849e44a94f878acd366449ed4edc",
    "Utilities_Viewer": "5c74a8e61dd84585b960b01aaff2d88e",
    "Subsidence": "9398af0aa54a44bd848d890dd76fced4",
    "Zoning": "b94ca45474b64173be0d7b036452b3d5",
    "Oil_Well_Finder": "3d380a2ffe9a4489ad878ee56fc66405",
}

service_urls = {}
for name, item_id in items.items():
    info = get_item_info(item_id)
    url = info.get("url", "N/A")
    service_urls[name] = url
    print(f"{name}: {url}")

with open(os.path.join(OUTPUT_DIR, "service_urls.json"), "w") as f:
    json.dump(service_urls, f, indent=2)
