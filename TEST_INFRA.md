# E2E Test Infra: OsintNeoAi OCGIS & APN Spatial Intelligence Platform

## 1. Dual Track Test Architecture
The test infrastructure establishes a decoupled, dual-track verification model adhering to the project engineering guidelines:
- **Track A (Test Engineering / E2E Specialist)**: Develops and maintains the opaque-box, multi-tier automated test suite (`tests/test_ocgis_scraper_e2e.py`) and schema verification engines (`scripts/verify_apn_dataset_schema.py`), deriving expected outputs strictly from authoritative requirements.
- **Track B (Feature Implementation / Worker Engine)**: Implements browser automation (`tools/ocgis_scraper.py`, `scripts/run_ocgis_spatial_scraper.py`), secret defense gates (`scripts/verify_secret_free.py`), and dataset persistence pipelines (`data/ocgis_historical_apn_data.json`).
- **Integration Boundary**: The test suite exercises features across isolated units, stress boundaries, pairwise interactions, and full real-world acceptance criteria without leaking internal implementation details.

---

## 2. Test Philosophy & Methodologies
- **Opaque-Box & Requirement-Driven**: All test fixtures and assertions derive directly from `ORIGINAL_REQUEST.md` (Header `## 2026-09-16T17:51:33Z`), `PROJECT.md`, and cadastral survey specifications.
- **Multi-Vector Methodologies**:
  1. **Category-Partition Testing**: Partition input spaces into equivalence classes (e.g. address formats, APN formats, radius bounds, coordinate envelopes).
  2. **Boundary Value Analysis (BVA)**: Stress testing edge conditions (0.0-mile radius, negative buffers, extreme latitude/longitude values, empty inputs, network timeouts).
  3. **Pairwise & Combinatorial Integration**: Cross-validating module interactions (Spatial Buffer + APN extraction + historical permit matching + screenshot verification + secret scan gate).
  4. **Real-World Workload Acceptance**: Full verification of the authoritative `17631 Cameron Ln` target nexus, Book 142 cadastral cluster, and high-resolution map rendering.

---

## 3. Feature Inventory & Coverage Matrix
Derived from `PROJECT.md` Feature Catalog and authoritative requirements:

| # | Feature | Source Specification | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Cross) | Tier 4 (Real-World) |
|---|---|---|:---:|:---:|:---:|:---:|
| 1 | Law 14 Pre-Action Git Snapshot | PROJECT.md §1 / Law 14 | ✓ | ✓ | ✓ | ✓ |
| 2 | Pre-Commit Secret Scanner | PROJECT.md §2 / R3 | ✓ | ✓ | ✓ | ✓ |
| 3 | OCGIS Landing Registration Automation | PROJECT.md §3 / R1 | ✓ | ✓ | — | ✓ |
| 4 | Map Viewer Navigation & Modal Dismissal | PROJECT.md §4 / R1 | ✓ | ✓ | — | ✓ |
| 5 | Spatial 0.25-Mile Boundary Query | PROJECT.md §5 / R1 | ✓ | ✓ | ✓ | ✓ |
| 6 | High-Resolution Map Rendering Screenshot | PROJECT.md §6 / R1 | ✓ | ✓ | ✓ | ✓ |
| 7 | APN Cluster Data Extraction | PROJECT.md §7 / R2 | ✓ | ✓ | ✓ | ✓ |
| 8 | Historical Permit Ingestion & Correlation | PROJECT.md §8 / R2 | ✓ | ✓ | ✓ | ✓ |
| 9 | Structured JSON Persistence | PROJECT.md §9 / R2 | ✓ | ✓ | ✓ | ✓ |
| 10| E2E Verification Suite (Tiers 1-4) | PROJECT.md §10 | ✓ | ✓ | ✓ | ✓ |
| 11| Post-Action Git Commit & Origin Push | PROJECT.md §11 / R3 | ✓ | — | ✓ | ✓ |

---

## 4. Multi-Tier Test Suite Structure (`tests/test_ocgis_scraper_e2e.py`)

### Tier 1: Feature Isolation & Contract Coverage
Validates the fundamental mechanics and contracts of each subsystem in isolation:
- `test_t1_scraper_interface_signature`: Validates `run_ocgis_spatial_scraper` callable interface and parameter contract.
- `test_t1_playwright_context_initialization`: Verifies Playwright context configuration (1920x1080 viewport, high-DPI device scale factor 2.0).
- `test_t1_registration_form_parameters`: Validates landing page access registration parameters (`#name`, `#email`, `#phone`, `#message`, enabling `#submitButton`).
- `test_t1_map_navigation_url_routing`: Asserts route transition from `/home/` to `/map-viewer?id=2` and `/map-viewer?id=4`.
- `test_t1_disclaimer_modal_selector`: Confirms detection selector and dismissal contract for Material-UI "Disclaimer" dialog.
- `test_t1_apn_normalization_standard`: Asserts deterministic normalization of 8-digit, 10-digit, and hyphenated APNs (`normalize_apn("14207333") -> "142-073-33"`).
- `test_t1_parcel_data_output_file_creation`: Verifies atomic JSON file write and disk serialization.
- `test_t1_screenshot_file_creation_dimensions`: Verifies PNG file header magic bytes (`\x89PNG\r\n\x1a\n`) and dimension validation.

### Tier 2: Boundary Value, Corner Cases & Fault Resilience
Stresses the system against abnormal, extreme, and malformed inputs:
- `test_t2_empty_and_whitespace_address`: Asserts descriptive validation error when target address is empty or whitespace.
- `test_t2_zero_and_negative_radius`: Tests handling of 0.0-mile radius (point query) and rejection of negative radius values.
- `test_t2_malformed_and_extreme_coordinates`: Validates rejection of out-of-range latitudes/longitudes and handling of origin `(0.0, 0.0)`.
- `test_t2_network_timeout_handling`: Verifies graceful retry and structured error recording during slow or unresponsive upstream GIS services.
- `test_t2_corrupted_json_resilience`: Verifies error reporting and fallback state when encountering corrupted or truncated JSON files.
- `test_t2_missing_dom_element_diagnostic_capture`: Confirms diagnostic capture to `scratch/ocgis_error_*.png` when unexpected DOM mutations occur.
- `test_t2_parcels_without_permits_empty_array`: Asserts parcels without permits default to empty list `[]` instead of null or missing key.
- `test_t2_atomic_write_crash_resilience`: Confirms atomic write pattern (`.tmp` write followed by `os.replace`) prevents partial or corrupted file artifacts.

### Tier 3: Cross-Feature Pairwise Combinations
Validates end-to-end data flow between interrelated modules:
- `test_t3_combo1_spatial_buffer_to_apn_extraction`: Spatial 0.25-mile buffer -> ArcGIS MapServer parcel query -> APN list extraction.
- `test_t3_combo2_apn_extraction_to_historical_permits`: APN extraction -> Accela permit matching (`B2020-005995`, `CO2020-005184`, `M2020-006464`) -> merged parcel permit record.
- `test_t3_combo3_screenshot_capture_to_artifact_manifest`: WebGL canvas capture -> `scratch/ocgis_map_cameron_radius.png` -> SHA-256 computation -> `artifacts.map_screenshot` entry.
- `test_t3_combo4_dataset_schema_validation_gate`: Full APN cluster dataset -> Draft-07 JSON Schema validation gate (`scripts/verify_apn_dataset_schema.py`).
- `test_t3_combo5_pre_commit_secret_scan_gate`: Staged artifacts -> `scripts/verify_secret_free.py` scanning -> 0 secret violations.
- `test_t3_combo6_law14_state_preservation_workflow`: Pre-action tag snapshot / `.bak` backup -> file write -> post-action git working tree verification.

### Tier 4: Real-World Workload & End-to-End Acceptance
Executes canonical real-world scenarios representing operational deployment:
- `test_t4_scenario1_cameron_ln_full_workflow`: End-to-end execution for `17631 Cameron Ln, Huntington Beach, CA 92647` (Lat: 33.715362, Lon: -117.989211, 0.25-mile radius).
- `test_t4_scenario2_book_142_apn_cluster_verification`: Cadastral verification of all 15 Book 142 parcels (`142-073-33`, `142-073-54`, `142-075-01`, `142-075-02`, `142-082-35`, `142-122-07`, `142-242-16`, etc.).
- `test_t4_scenario3_historical_permits_mercy_house`: Verification of Navigation Center permits (`B2020-005995`, `CO2020-005184`, `M2020-006464`) associated with `142-073-33`.
- `test_t4_scenario4_draft07_schema_conformance`: Schema compliance verification of `data/ocgis_historical_apn_data.json` against the Draft-07 specification.
- `test_t4_scenario5_valid_non_empty_map_screenshot`: Physical file verification of `scratch/ocgis_map_cameron_radius.png` (non-empty PNG, >50 KB, valid PNG signature).

---

## 5. Test Environment & Execution Commands

### Python Environment
- **Path**: `C:\Users\Amd949609\.local\bin\python.exe`
- **Engine**: Python 3.12, Playwright 1.62.0, Chromium 1234, Pytest 9.1.1, Jsonschema 4.26.0

### Test Execution Commands
- **Test Collection & Syntax Verification**:
  ```powershell
  & "C:\Users\Amd949609\.local\bin\python.exe" -m pytest tests/test_ocgis_scraper_e2e.py --collect-only
  ```
- **Complete Test Suite Run (Verbose)**:
  ```powershell
  & "C:\Users\Amd949609\.local\bin\python.exe" -m pytest tests/test_ocgis_scraper_e2e.py -v
  ```
- **Tier-Specific Execution**:
  ```powershell
  & "C:\Users\Amd949609\.local\bin\python.exe" -m pytest tests/test_ocgis_scraper_e2e.py -k "TestTier1" -v
  & "C:\Users\Amd949609\.local\bin\python.exe" -m pytest tests/test_ocgis_scraper_e2e.py -k "TestTier2" -v
  & "C:\Users\Amd949609\.local\bin\python.exe" -m pytest tests/test_ocgis_scraper_e2e.py -k "TestTier3" -v
  & "C:\Users\Amd949609\.local\bin\python.exe" -m pytest tests/test_ocgis_scraper_e2e.py -k "TestTier4" -v
  ```
- **Standalone Schema Validation**:
  ```powershell
  & "C:\Users\Amd949609\.local\bin\python.exe" scripts/verify_apn_dataset_schema.py
  & "C:\Users\Amd949609\.local\bin\python.exe" scripts/verify_apn_dataset_schema.py --sample
  ```

---

## 6. Quality Gates & Certification Standards
1. **Schema Gate**: `data/ocgis_historical_apn_data.json` must strictly validate against `DRAFT07_APN_DATASET_SCHEMA` with 0 validation errors.
2. **Visual Evidence Gate**: `scratch/ocgis_map_cameron_radius.png` must exist, be a valid PNG (`b'\x89PNG\r\n\x1a\n'`), have file size > 50 KB, and show the target radius rendering.
3. **Secret Defense Gate**: Pre-commit scanner must detect 0 instances of Google/Gemini API keys, private keys, JWTs, AWS keys, or Azure connection strings before staging.
4. **Law 14 Integrity Gate**: Git pre-action tag and `.bak` file must exist before modifying files; git status must be clean after synchronization.
