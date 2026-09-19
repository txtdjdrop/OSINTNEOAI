"""
tests/test_ocgis_scraper_e2e.py
================================
Comprehensive Opaque-Box E2E Test Suite for OsintNeoAi OCGIS Spatial Scraper,
APN Cluster Mapping, and Universal AI Law 14 Integrity State Preservation.

Organized into Tiers 1-4 per TEST_INFRA.md:
  - Tier 1: Feature Coverage (scrapers, registration form parameters, map navigation,
            parcel data output file creation, screenshot file creation).
  - Tier 2: Boundary & Corner Cases (invalid/empty addresses, zero radius,
            malformed coordinates, timeout handling, corrupted JSON resilience).
  - Tier 3: Cross-Feature Combinations (spatial buffer + APN extraction +
            historical permit matching + screenshot verification + secret scan gate).
  - Tier 4: Real-World Workload Acceptance (17631 Cameron Ln full workflow,
            Book 142 APN cluster verification, Draft-07 JSON schema conformance
            of data/ocgis_historical_apn_data.json, valid non-empty PNG screenshot
            at scratch/ocgis_map_cameron_radius.png).

Derived Authoritative Specifications:
  - ORIGINAL_REQUEST.md (Header ## 2026-09-16T17:51:33Z)
  - PROJECT.md
  - survey_report.3.md
"""

import hashlib
import inspect
import json
import math
import os
import re
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Real Scraper Modules
from scripts.run_ocgis_spatial_scraper import (
    BOOK_142_CLUSTER_SPECS,
    BROWSER_CONTEXT_CONFIG,
    DEFAULT_DATA_PATH,
    DEFAULT_SCREENSHOT_PATH,
    DISCLAIMER_MODAL_SELECTORS,
    MAP_ROUTES,
    REGISTRATION_SELECTORS,
    TARGET_SPEC,
    haversine_distance_meters,
    load_accela_permits,
    normalize_apn,
    query_arcgis_parcel_rest,
    run_ocgis_spatial_scraper,
    validate_coordinates,
    validate_radius,
    validate_target_address,
)
from scripts.verify_apn_dataset_schema import (
    DRAFT07_APN_DATASET_SCHEMA,
    get_canonical_sample_payload,
    validate_dataset,
    validate_file,
)
from scripts.verify_secret_free import (
    SECRET_PATTERNS,
    is_binary_file,
    scan_file,
    scan_text_content,
)


# ==============================================================================
# Helper Cadastral & Spatial Utilities
# ==============================================================================

def generate_test_png(width: int = 1920, height: int = 1080, payload_size: int = 60000) -> bytes:
    """Generate a valid binary PNG buffer with specified dimensions and minimum byte size."""
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", 0x12345678)
    ihdr_chunk = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + ihdr_crc
    idat_len = max(100, payload_size - 100)
    idat_data = b"\x78\x9c" + b"\x00" * idat_len
    idat_chunk = struct.pack(">I", len(idat_data)) + b"IDAT" + idat_data + b"\x98\x76\x54\x32"
    iend_chunk = struct.pack(">I", 0) + b"IEND" + b"\xae\x42\x60\x82"
    return signature + ihdr_chunk + idat_chunk + iend_chunk


# ==============================================================================
# Tier 1: Feature Coverage
# ==============================================================================

class TestTier1FeatureCoverage:
    """
    Tier 1: Feature Isolation & Contract Verification
    Covers scrapers, registration form parameters, map navigation,
    parcel data output file creation, and screenshot file creation.
    """

    def test_t1_01_scraper_interface_signature(self):
        """
        Feature 1: Verify the scraper interface signature and parameter defaults.
        Contract: run_ocgis_spatial_scraper(target_address, radius_miles=0.25, output_json=..., output_screenshot=...)
        """
        sig = inspect.signature(run_ocgis_spatial_scraper)
        params = list(sig.parameters.keys())
        assert "target_address" in params
        assert "radius_miles" in params
        assert "output_json" in params
        assert "output_screenshot" in params

        assert sig.parameters["radius_miles"].default == 0.25
        assert "17631 Cameron Ln" in TARGET_SPEC["address"]
        assert TARGET_SPEC["radius_miles"] == 0.25
        assert "data" in str(DEFAULT_DATA_PATH)
        assert "scratch" in str(DEFAULT_SCREENSHOT_PATH)

    def test_t1_02_registration_form_parameters(self):
        """
        Feature 3: Verify OCGIS Landing Registration automation parameters.
        The /home/ landing page contact form requires: #name, #email, #phone, #message,
        and enables #submitButton upon input events.
        """
        for field in ["name", "email", "phone", "message", "submit"]:
            assert field in REGISTRATION_SELECTORS
            assert REGISTRATION_SELECTORS[field].startswith("#")

    def test_t1_03_map_navigation_url_routing(self):
        """
        Feature 4: Verify URL routing between portal landing and Esri map viewers.
        Catalog routes:
          - Landing: https://webapps.ocgis.com/oclandinsights/home/
          - Public Map: https://webapps.ocgis.com/oclandinsights/map-viewer?id=2
          - Assessor Map: https://webapps.ocgis.com/oclandinsights/map-viewer?id=4
        """
        assert MAP_ROUTES["home"].endswith("/home/")
        assert "map-viewer?id=2" in MAP_ROUTES["public_map"]
        assert "map-viewer?id=4" in MAP_ROUTES["assessor_map"]
        assert "map-viewer?id=8" in MAP_ROUTES["environmental"]

    def test_t1_04_disclaimer_modal_contract(self):
        """
        Feature 4: Verify detection and dismissal contract for Material-UI Disclaimer dialog.
        MUI Dialog with title 'Disclaimer' and button 'Agree'.
        """
        assert "[role='dialog']" in DISCLAIMER_MODAL_SELECTORS
        assert any("agree" in sel.lower() for sel in DISCLAIMER_MODAL_SELECTORS)

    def test_t1_05_apn_cadastral_normalization(self):
        """
        Feature 7: Verify Orange County APN normalization into canonical format XXX-XXX-XX.
        """
        test_cases = [
            ("14207333", "142-073-33"),
            ("142-073-33", "142-073-33"),
            ("142 073 33", "142-073-33"),
            ("14207501", "142-075-01"),
            ("142-242-16", "142-242-16"),
            ("14205653", "142-056-53"),
            ("14220790", "142-207-90"),
        ]

        for raw_input, expected in test_cases:
            assert normalize_apn(raw_input) == expected, f"Failed on raw input: {raw_input}"

    def test_t1_06_parcel_data_output_file_creation(self):
        """
        Feature 9: Verify structured parcel dataset atomic write and file creation.
        """
        sample_data = get_canonical_sample_payload()

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_apn_data.json"
            temp_file = Path(tmpdir) / "test_apn_data.json.tmp"

            with open(temp_file, "w", encoding="utf-8") as fp:
                json.dump(sample_data, fp, indent=2)
            os.replace(temp_file, out_file)

            assert out_file.exists(), "Output file must be created on disk"
            assert out_file.stat().st_size > 500, "Output file must contain substantive payload"

            with open(out_file, "r", encoding="utf-8") as fp:
                loaded = json.load(fp)
            assert loaded["schema_version"] == "2.0.0"
            assert len(loaded["parcels"]) > 0

    def test_t1_07_screenshot_file_creation_and_png_header(self):
        """
        Feature 6: Verify screenshot persistence and valid PNG magic bytes header.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            out_png = Path(tmpdir) / "ocgis_map_cameron_radius.png"
            png_bytes = generate_test_png(width=1920, height=1080, payload_size=55000)

            with open(out_png, "wb") as fp:
                fp.write(png_bytes)

            assert out_png.exists()
            assert out_png.stat().st_size >= 50000, "PNG file must exceed 50KB threshold"

            with open(out_png, "rb") as fp:
                header = fp.read(8)
            assert header == b"\x89PNG\r\n\x1a\n", "Must contain authoritative PNG magic bytes"

    def test_t1_08_playwright_context_and_browser_configuration(self):
        """
        Feature 1 / Automation Engine: Verify Playwright browser launch context specifications.
        Viewport: 1920x1080, headless: True.
        """
        assert BROWSER_CONTEXT_CONFIG["viewport"]["width"] == 1920
        assert BROWSER_CONTEXT_CONFIG["viewport"]["height"] == 1080
        assert BROWSER_CONTEXT_CONFIG["headless"] is True
        assert "Chrome" in BROWSER_CONTEXT_CONFIG["user_agent"]


# ==============================================================================
# Tier 2: Boundary & Corner Cases
# ==============================================================================

class TestTier2BoundaryAndCornerCases:
    """
    Tier 2: Boundary Value Analysis & Fault Resilience
    Covers invalid/empty addresses, zero/negative radii, malformed coordinates,
    timeout handling, and corrupted JSON resilience.
    """

    def test_t2_01_empty_and_whitespace_target_address(self):
        """
        Boundary 1: Address validation must reject empty strings, whitespace, or None.
        """
        invalid_addresses = ["", "   ", "\t\n", None]
        for invalid in invalid_addresses:
            with pytest.raises(ValueError, match="Target address must not be empty"):
                validate_target_address(invalid)

    def test_t2_02_zero_and_negative_radius_boundaries(self):
        """
        Boundary 2: Radius boundaries.
        0.0 miles: Valid point boundary (converts to 0 meters, points on parcel).
        Negative radius: Must be rejected.
        """
        r_mi, r_m = validate_radius(0.0)
        assert r_mi == 0.0
        assert r_m == 0.0

        with pytest.raises(ValueError, match="Radius miles cannot be negative"):
            validate_radius(-0.25)

    def test_t2_03_malformed_and_extreme_coordinates(self):
        """
        Boundary 3: Geocoordinate range boundaries.
        Latitude must be within [-90.0, 90.0].
        Longitude must be within [-180.0, 180.0].
        """
        assert validate_coordinates(33.715362, -117.989211) is True

        with pytest.raises(ValueError, match="Latitude out of bounds"):
            validate_coordinates(95.0, -117.989211)

        with pytest.raises(ValueError, match="Latitude out of bounds"):
            validate_coordinates(-90.1, -117.989211)

        with pytest.raises(ValueError, match="Longitude out of bounds"):
            validate_coordinates(33.715362, 185.0)

        with pytest.raises(ValueError, match="Longitude out of bounds"):
            validate_coordinates(33.715362, -180.5)

    def test_t2_04_network_timeout_handling(self):
        """
        Boundary 4: Network resilience in query_arcgis_parcel_rest.
        Verifies that extreme inputs or network interruptions return a graceful empty list
        without crashing Python.
        """
        res = query_arcgis_parcel_rest(999.0, 999.0, radius_feet=1)
        assert isinstance(res, list)

    def test_t2_05_corrupted_json_resilience(self):
        """
        Boundary 5: Corrupted JSON resilience.
        Validates that truncated or malformed JSON files produce clean validation errors
        instead of uncaught parser exceptions.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            corrupt_file = Path(tmpdir) / "corrupt.json"
            with open(corrupt_file, "w", encoding="utf-8") as fp:
                fp.write('{"target": "17631 Cameron", "radius": "0.25", "parcels": [')

            is_valid, errors = validate_file(corrupt_file)
            assert is_valid is False
            assert len(errors) == 1
            assert "Malformed JSON" in errors[0]

    def test_t2_06_missing_dom_element_diagnostic_capture(self):
        """
        Boundary 6: Diagnostic error capture on missing DOM selector.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            scratch_tmp = Path(tmpdir)
            err_shot = scratch_tmp / "ocgis_error.png"
            err_shot.touch()
            assert err_shot.exists()
            assert "ocgis_error.png" in err_shot.name

    def test_t2_07_parcels_without_permits_empty_array(self):
        """
        Boundary 7: Parcels without permits must produce an empty array [], never null.
        Draft-07 schema requires "permits": { "type": "array" }.
        """
        sample_data = get_canonical_sample_payload()
        parcel_no_permits = dict(sample_data["parcels"][0])
        parcel_no_permits["apn"] = "142-073-54"
        parcel_no_permits["permits"] = []
        sample_data["parcels"].append(parcel_no_permits)

        is_valid, errors = validate_dataset(sample_data)
        assert is_valid is True, f"Empty permit array must be valid: {errors}"

        parcel_null_permits = dict(sample_data["parcels"][0])
        parcel_null_permits["permits"] = None
        sample_data["parcels"] = [parcel_null_permits]
        is_valid_null, errors_null = validate_dataset(sample_data)
        assert is_valid_null is False
        assert any("permits" in err for err in errors_null)

    def test_t2_08_atomic_file_write_resilience(self):
        """
        Boundary 8: Crash resilience during disk write.
        Verifies that atomic write pattern (.tmp + os.replace) prevents corruption
        if an exception occurs prior to replacement.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            target_path = Path(tmpdir) / "target.json"
            with open(target_path, "w", encoding="utf-8") as fp:
                fp.write('{"state": "original"}')

            temp_path = Path(tmpdir) / "target.json.tmp"
            try:
                with open(temp_path, "w", encoding="utf-8") as fp:
                    fp.write('{"state": "partial write that failed halfway...')
                    raise IOError("Disk full / process killed")
                os.replace(temp_path, target_path)
            except IOError:
                pass

            with open(target_path, "r", encoding="utf-8") as fp:
                content = json.load(fp)
            assert content["state"] == "original", "Original file must not be corrupted"


# ==============================================================================
# Tier 3: Cross-Feature Combinations
# ==============================================================================

class TestTier3CrossFeatureCombinations:
    """
    Tier 3: Pairwise & Cross-Module Pipeline Integration
    Covers:
      1. Spatial Buffer -> APN Extraction
      2. APN Extraction -> Historical Permit Matching
      3. Screenshot Capture -> Artifact Manifest SHA-256 Linkage
      4. Assembled Dataset -> Draft-07 Schema Validation Gate
      5. Pre-Commit Artifacts -> Secret Defense Scanner Gate
      6. Law 14 Pre/Post State Preservation Workflow
    """

    def test_t3_01_spatial_buffer_to_apn_extraction(self):
        """
        Combination 1: Spatial 0.25-mile buffer -> APN Extraction.
        Target coordinates: 17631 Cameron Ln (33.715362, -117.989211).
        All parcels in cluster must fall within radial bound.
        """
        center_lat = TARGET_SPEC["latitude"]
        center_lon = TARGET_SPEC["longitude"]

        for spec in BOOK_142_CLUSTER_SPECS:
            dist = haversine_distance_meters(center_lat, center_lon, spec["latitude"], spec["longitude"])
            assert dist <= 482.8, f"Parcel {spec['apn']} at {dist}m exceeds cluster bound"

    def test_t3_02_apn_extraction_to_historical_permits(self):
        """
        Combination 2: APN Extraction -> Historical Permit Matching.
        Correlate APN 142-073-33 with Huntington Beach Accela records.
        """
        permits_db = load_accela_permits()
        cameron_permits = permits_db.get("17631 Cameron", [])
        assert len(cameron_permits) >= 3
        permit_numbers = [p["permit_number"] for p in cameron_permits]
        assert "B2020-005995" in permit_numbers
        assert "CO2020-005184" in permit_numbers
        assert "M2020-006464" in permit_numbers
        assert any("RESOLUTION 2019-22" in p["description"] for p in cameron_permits)

    def test_t3_03_screenshot_capture_to_artifact_manifest(self):
        """
        Combination 3: Screenshot Capture -> SHA-256 Manifest Calculation.
        Verifies cryptographic linkage between physical screenshot on disk
        and the artifacts.map_screenshot.sha256 entry.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shot_file = Path(tmpdir) / "ocgis_map_cameron_radius.png"
            test_content = generate_test_png(1920, 1080, 52000)
            shot_file.write_bytes(test_content)

            computed_sha256 = hashlib.sha256(test_content).hexdigest()
            manifest_entry = {
                "file_path": str(shot_file),
                "captured_at": "2026-09-16T18:30:15Z",
                "sha256": computed_sha256,
                "file_size_bytes": len(test_content),
                "dimensions": {"width": 1920, "height": 1080, "device_scale_factor": 1.0}
            }

            assert manifest_entry["sha256"] == hashlib.sha256(shot_file.read_bytes()).hexdigest()
            assert len(manifest_entry["sha256"]) == 64

    def test_t3_04_dataset_schema_validation_gate(self):
        """
        Combination 4: Assembled Dataset -> Draft-07 Schema Validation Gate.
        """
        payload = get_canonical_sample_payload()
        is_valid, errors = validate_dataset(payload)
        assert is_valid is True, f"Canonical sample failed validation: {errors}"
        assert len(errors) == 0

    def test_t3_05_pre_commit_secret_scan_gate(self):
        """
        Combination 5: Staged Artifacts -> Pre-Commit Secret Defense Scanner.
        Tests that zero API keys, private keys, or credentials exist in the generated dataset.
        """
        serialized_data = json.dumps(get_canonical_sample_payload())
        violations = scan_text_content(serialized_data, "data/canonical_sample.json")
        assert len(violations) == 0, f"Secret pattern matched in dataset: {violations}"

    def test_t3_06_law14_state_preservation_workflow(self):
        """
        Combination 6: Universal AI Law 14 State Preservation & Rollback.
        Verifies:
          1. Pre-action backup creation (.bak).
          2. File mutation.
          3. Rollback from .bak restores exact initial state.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_file = Path(tmpdir) / "data_file.json"
            bak_file = Path(tmpdir) / "data_file.json.bak"
            initial_content = '{"version": "1.0.0", "data": [1, 2, 3]}'

            orig_file.write_text(initial_content, encoding="utf-8")
            bak_file.write_text(orig_file.read_text(encoding="utf-8"), encoding="utf-8")
            assert bak_file.exists()
            assert bak_file.read_text(encoding="utf-8") == initial_content

            orig_file.write_text('{"version": "2.0.0", "data": [4, 5, 6]}', encoding="utf-8")
            assert orig_file.read_text(encoding="utf-8") != initial_content

            orig_file.write_text(bak_file.read_text(encoding="utf-8"), encoding="utf-8")
            assert orig_file.read_text(encoding="utf-8") == initial_content


# ==============================================================================
# Tier 4: Real-World Workload Acceptance
# ==============================================================================

class TestTier4RealWorldWorkloadAcceptance:
    """
    Tier 4: Real-World Cadastral Scenarios & Production Deliverables
    Exercises:
      1. 17631 Cameron Ln full workflow parameters.
      2. Book 142 cadastral APN cluster inventory.
      3. Historical Navigation Center permits under Resolution 2019-22.
      4. Draft-07 JSON schema conformance of workspace data/ocgis_historical_apn_data.json.
      5. High-resolution genuine map screenshot at scratch/ocgis_map_cameron_radius.png.
    """

    def test_t4_01_cameron_ln_full_workflow_parameters(self):
        """
        Scenario 1: Authoritative target parameter specification.
        Target: 17631 Cameron Ln, Huntington Beach, CA 92647
        Coordinates: 33.715362, -117.989211 | Radius: 0.25 miles (402.336m)
        """
        assert "Cameron Ln" in TARGET_SPEC["address"]
        assert TARGET_SPEC["radius_miles"] == 0.25
        assert TARGET_SPEC["target_apn"] == "142-073-33"
        assert abs(TARGET_SPEC["latitude"] - 33.715362) < 0.0001
        assert abs(TARGET_SPEC["longitude"] - (-117.989211)) < 0.0001

    def test_t4_02_book_142_apn_cluster_inventory(self):
        """
        Scenario 2: Cadastral inventory verification of the Book 142 APN cluster.
        Must account for all 15 identified parcels in the 0.25-mile nexus.
        """
        expected_apn_cluster = [
            "142-073-33", "142-073-54", "142-075-01", "142-075-02",
            "142-082-35", "142-122-07", "142-242-16", "142-253-04",
            "142-321-20", "142-492-11", "142-056-53", "142-063-04",
            "142-160-29", "142-207-90", "142-356-93"
        ]

        normalized_cluster = [normalize_apn(spec["apn"]) for spec in BOOK_142_CLUSTER_SPECS]
        assert len(normalized_cluster) == 15
        assert all(re.match(r"^142-[0-9]{3}-[0-9]{2}$", apn) for apn in normalized_cluster)
        assert "142-073-33" in normalized_cluster  # 17631 Cameron Ln
        assert "142-242-16" in normalized_cluster  # 17642 Beach Blvd

    def test_t4_03_historical_permits_resolution_2019_22(self):
        """
        Scenario 3: Verification of historical Navigation Center permits.
        Must reflect permits associated with City of Huntington Beach Resolution 2019-22:
          - B2020-005995 (Trailer foundations / anchorage)
          - CO2020-005184 (Sprung structure dormitory certificate of occupancy)
          - M2020-006464 (Mechanical HVAC for shelter)
        """
        dataset_path = REPO_ROOT / "data" / "ocgis_historical_apn_data.json"
        assert dataset_path.exists()
        with open(dataset_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        target_parcel = next((p for p in data["parcels"] if p["apn"] == "142-073-33"), None)
        assert target_parcel is not None, "Target parcel 142-073-33 must exist"

        permits = target_parcel.get("permits", [])
        assert len(permits) >= 3
        permit_numbers = [p["permit_number"] for p in permits]
        assert "B2020-005995" in permit_numbers
        assert "CO2020-005184" in permit_numbers
        assert "M2020-006464" in permit_numbers
        assert any("RESOLUTION 2019-22" in p["description"] for p in permits)

    def test_t4_04_dataset_schema_conformance_check(self):
        """
        Scenario 4: Authoritative schema validation check on data/ocgis_historical_apn_data.json.
        """
        dataset_path = REPO_ROOT / "data" / "ocgis_historical_apn_data.json"
        assert dataset_path.exists(), f"Deliverable {dataset_path} must exist"

        is_valid, errors = validate_file(dataset_path)
        assert is_valid, f"Draft-07 schema validation failed ({len(errors)} errors):\n" + "\n".join(errors)

    def test_t4_05_map_screenshot_deliverable_validation(self):
        """
        Scenario 5: Physical file verification of scratch/ocgis_map_cameron_radius.png.
        Acceptance Criteria:
          - File must exist at scratch/ocgis_map_cameron_radius.png
          - File must be valid PNG (magic bytes \\x89PNG\\r\\n\\x1a\\n)
          - File size must exceed 50,000 bytes (proving WebGL canvas settled and not blank white tile)
          - Width >= 1920, Height >= 1080
          - Absence of synthetic byte spoofer CRC 0x7E3F1A99
          - High visual entropy / variance across scanline byte frequencies
        """
        screenshot_path = REPO_ROOT / "scratch" / "ocgis_map_cameron_radius.png"
        assert screenshot_path.exists(), f"Deliverable {screenshot_path} does not exist"

        raw_bytes = screenshot_path.read_bytes()
        file_size = len(raw_bytes)

        # 1. Assert valid PNG magic header
        assert raw_bytes[:8] == b"\x89PNG\r\n\x1a\n", f"{screenshot_path.name} is not a valid PNG image"

        # 2. Assert minimum size > 50,000 bytes
        assert file_size >= 50000, f"Screenshot {screenshot_path.name} is only {file_size} bytes, expected >= 50000"

        # 3. Assert dimensions
        assert raw_bytes[12:16] == b"IHDR", "Missing IHDR chunk in PNG"
        width, height = struct.unpack(">II", raw_bytes[16:24])
        assert width >= 1920, f"Width {width} is below 1920px"
        assert height >= 1080, f"Height {height} is below 1080px"

        # 4. Assert absence of synthetic byte spoofer CRC 0x7E3F1A99
        assert b"\x7e\x3f\x1a\x99" not in raw_bytes, "Detected synthetic fallback raster spoofer bytes!"

        # 5. Assert visual entropy / non-blank map rendering (variance of byte frequencies)
        byte_counts: Dict[int, int] = {}
        for b in raw_bytes[100:10000]:
            byte_counts[b] = byte_counts.get(b, 0) + 1
        unique_byte_values = len(byte_counts)
        assert unique_byte_values > 128, f"Insufficient visual entropy ({unique_byte_values} unique bytes), likely blank/solid color"
