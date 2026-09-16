# Project: OsintNeoAi OCGIS & APN Spatial Intelligence Platform

## Architecture
The OsintNeoAi spatial intelligence enhancement integrates Playwright headless browser automation, ArcGIS MapServer spatial queries, and multi-vector forensic OSINT permit correlation into structured persistence and automated git state preservation.

- **Automation Engine**: Playwright 1.62.0 running via `C:\Users\Amd949609\.local\bin\python.exe` with pre-installed Chromium binary (`chrome-win64\chrome.exe`).
- **Spatial Target**: `17631 Cameron Ln, Huntington Beach, CA 92647` (Lat: `33.715362`, Lon: `-117.989211`) and its 0.25-mile (1,320 ft / 402.34m) radial buffer encompassing the Book 142 APN cluster adjoining the 17642 Beach Blvd Superfund site.
- **Data Persistence**: Structured JSON schema output at `data/ocgis_historical_apn_data.json` and high-resolution rendering screenshots at `scratch/ocgis_map_cameron_radius.png`.
- **Integrity & State Preservation**: Universal AI Law 14 pre-action snapshot tagging, atomic `.bak` preservation, automated pre-commit secret scanning, and clean push to `origin/main`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Law 14 Pre-Action Git Snapshot | Create reversible git tags and atomic `.bak` file snapshots before modifications | M1 | Survey 1 & 3 |
| 2 | Pre-Commit Secret Scanner | Implement `scripts/verify_secret_free.py` to scan staged files for API keys, tokens, and credentials | M1 | Survey 1 & 3 |
| 3 | OCGIS Landing Registration Automation | Playwright automation to fill `#name`, `#email`, `#phone`, `#message` on `/home/` and enable `#submitButton` | M2 | Survey 1 & 2 |
| 4 | Map Viewer Navigation & Modal Dismissal | Navigate to `/map-viewer?id=2` and dismiss the Material-UI Disclaimer dialog by clicking "Agree" | M2 | Survey 1, 2, 3 |
| 5 | Spatial 0.25-Mile Boundary Query | Query ArcGIS MapServer parcel layer with 0.25-mile (1320 ft) buffer around target coordinates | M2 | Survey 2 & 3 |
| 6 | High-Resolution Map Rendering Screenshot | Wait for WebGL canvas settling (`view.stationary === true`) and save screenshot to `scratch/ocgis_map_cameron_radius.png` | M2 | Survey 1, 2, 3 |
| 7 | APN Cluster Data Extraction | Extract parcel attributes, AssessmentNo, Situs addresses, and WGS84 geometry for Book 142 parcels | M3 | Survey 2 & 3 |
| 8 | Historical Permit Ingestion & Correlation | Correlate municipal permits (`B2020-005995`, `CO2020-005184`, `M2020-006464`, etc.) with APN cluster | M3 | Survey 3 |
| 9 | Structured JSON Persistence | Persist complete APN cluster dataset to `data/ocgis_historical_apn_data.json` conforming to Draft-07 schema | M3 | Survey 3 |
| 10 | E2E Verification Suite (Tiers 1-4) | Opaque-box requirement-driven test suite validating scraping, schema, screenshots, and git state | M4 / E2E Track | Survey 3 |
| 11 | Post-Action Git Commit & Origin Push | Push clean code, screenshots, and datasets to `origin/main` without secret protection violations | M4 | Survey 1 & 3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Git State Preservation & Secret Defense | Law 14 pre-action snapshot tagging, atomic backups, and pre-commit secret scanning engine | none | PLANNED |
| M2 | OCGIS Headless Scraper & Map Capture | Playwright automation of registration modal, map viewer navigation, 0.25m spatial query, and `scratch/` map capture | M1 | PLANNED |
| M3 | APN Cluster Structuring & Persistence | Parcel attribute parsing, historical permit correlation, and persistence to `data/ocgis_historical_apn_data.json` | M2 | PLANNED |
| M4 | Final Integration & E2E Verification | 100% E2E test suite pass (Tiers 1-4), clean git commit and push to `origin/main` | M1, M2, M3 | PLANNED |

## Interface Contracts
### Scraper ↔ Data Persistence
- Function: `run_ocgis_spatial_scraper(target_address, radius_miles, output_json, output_screenshot)`
- Output JSON Schema: `data/ocgis_historical_apn_data.json` conforming to Draft-07 specification.
- Screenshot output: `scratch/ocgis_map_cameron_radius.png` (PNG format, min 1920x1080 resolution).

### Scraper ↔ OCGIS MapServer REST API
- Base Parcels Service: `https://www.ocgis.com/arcpub/rest/services/Map_Layers/Parcels/MapServer/0/query`
- Spatial Buffer: `distance=1320`, `units=esriSRUnit_Foot`, `geometryType=esriGeometryPoint`, `spatialRel=esriSpatialRelIntersects`
- Coordinate Projection: `outSpatialReference={"wkid": 4326}` for WGS84 GeoJSON output.

### Secret Scanner ↔ Git Pre-Commit Gate
- Command: `python scripts/verify_secret_free.py`
- Exit Code: 0 (No secrets found), 1 (Violation detected — commit blocked).

## Code Layout
- `scripts/run_ocgis_spatial_scraper.py`: Main Playwright and ArcGIS scraper implementing R1 and R2.
- `scripts/verify_secret_free.py`: Secret scanning and credential protection validator implementing R3.
- `scripts/verify_apn_dataset_schema.py`: Schema validator for `data/ocgis_historical_apn_data.json`.
- `tests/test_ocgis_scraper_e2e.py`: Opaque-box E2E test suite (Tiers 1-4).
- `data/ocgis_historical_apn_data.json`: Output APN cluster dataset.
- `scratch/ocgis_map_cameron_radius.png`: Output map rendering screenshot.
