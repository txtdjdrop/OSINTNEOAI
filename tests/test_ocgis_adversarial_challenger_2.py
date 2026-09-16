"""
tests/test_ocgis_adversarial_challenger_2.py
============================================
Adversarial Stress Test Suite & Empirical Verification Harness
Author: teamwork_preview_challenger_2 (EMPIRICAL CHALLENGER)
Project: OsintNeoAi - OCGIS Spatial Scraper & APN Cluster Intelligence

Tests stress boundaries, malformed inputs, coordinate envelopes,
APN normalization edge cases, secret defense scanner penetration,
JSON schema invariants, and real-world artifact integrity.
"""

import hashlib
import json
import math
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_ocgis_spatial_scraper import (
    BOOK_142_CLUSTER_SPECS,
    TARGET_SPEC,
    haversine_distance_meters,
    normalize_apn,
    run_ocgis_spatial_scraper,
)
from scripts.verify_apn_dataset_schema import (
    DRAFT07_APN_DATASET_SCHEMA,
    validate_dataset,
    validate_file,
)
from scripts.verify_secret_free import (
    SECRET_PATTERNS,
    is_binary_file,
    scan_text_content,
)


# ==============================================================================
# 1. Adversarial Address & Radius Boundary Testing
# ==============================================================================

class TestAdversarialInputValidation:
    """Stress tests parameter validation and boundary handling."""

    @pytest.mark.parametrize("bad_address", [
        "",
        "   ",
        "\t\n\r",
        "         \n  ",
    ])
    def test_empty_or_whitespace_address_raises_value_error(self, bad_address: str):
        with pytest.raises(ValueError, match="Target address must not be empty or whitespace"):
            run_ocgis_spatial_scraper(target_address=bad_address)

    @pytest.mark.parametrize("neg_radius", [
        -0.0001,
        -0.25,
        -1.0,
        -999.9,
    ])
    def test_negative_radius_raises_value_error(self, neg_radius: float):
        with pytest.raises(ValueError, match="Radius miles cannot be negative"):
            run_ocgis_spatial_scraper(
                target_address="17631 Cameron Ln, Huntington Beach, CA 92647",
                radius_miles=neg_radius
            )

    def test_zero_radius_accepted_as_point_query(self, monkeypatch):
        """0.0 radius represents an exact point query without spatial expansion."""
        tmp_json = REPO_ROOT / "scratch" / "test_zero_radius.json"
        tmp_scr = REPO_ROOT / "scratch" / "test_zero_radius.png"
        monkeypatch.setattr(
            "scripts.run_ocgis_spatial_scraper.run_playwright_automation",
            lambda path: False
        )
        try:
            res = run_ocgis_spatial_scraper(
                target_address="17631 Cameron Ln, Huntington Beach, CA 92647",
                radius_miles=0.0,
                output_json=str(tmp_json),
                output_screenshot=str(tmp_scr),
            )
            assert res["query_parameters"]["spatial_buffer"]["radius_miles"] == 0.0
            assert res["query_parameters"]["spatial_buffer"]["radius_meters"] == 0.0
            assert tmp_json.exists()
        finally:
            if tmp_json.exists():
                tmp_json.unlink()
            if tmp_scr.exists():
                tmp_scr.unlink()

    @pytest.mark.parametrize("fuzzed_address", [
        "'; DROP TABLE parcels; --",
        "<script>alert('xss')</script>",
        "17631 Cameron Ln\x00Huntington Beach",
        "A" * 5000,
    ])
    def test_fuzzed_addresses_handled_without_crash(self, fuzzed_address: str, monkeypatch):
        """Fuzzed/hostile address strings should be accepted or safely processed without crashing Python."""
        tmp_json = REPO_ROOT / "scratch" / "test_fuzzed_addr.json"
        tmp_scr = REPO_ROOT / "scratch" / "test_fuzzed_addr.png"
        monkeypatch.setattr(
            "scripts.run_ocgis_spatial_scraper.run_playwright_automation",
            lambda path: False
        )
        try:
            res = run_ocgis_spatial_scraper(
                target_address=fuzzed_address,
                radius_miles=0.25,
                output_json=str(tmp_json),
                output_screenshot=str(tmp_scr),
            )
            assert res["query_parameters"]["target_address"] == fuzzed_address
        finally:
            if tmp_json.exists():
                tmp_json.unlink()
            if tmp_scr.exists():
                tmp_scr.unlink()


# ==============================================================================
# 2. Geodesic Distance & Coordinate Envelopes
# ==============================================================================

class TestAdversarialSpatialCoordinates:
    """Stress tests geodetic distance calculations and edge coordinates."""

    def test_haversine_identical_points_is_zero(self):
        dist = haversine_distance_meters(33.715362, -117.989211, 33.715362, -117.989211)
        assert dist == 0.0

    def test_haversine_polar_and_equatorial_bounds(self):
        # North Pole to South Pole: ~20,015 km (half Earth circumference)
        dist_poles = haversine_distance_meters(90.0, 0.0, -90.0, 0.0)
        assert 20_000_000 < dist_poles < 20_050_000

        # Equator quarter circle (0,0) to (0,90): ~10,007 km
        dist_equator = haversine_distance_meters(0.0, 0.0, 0.0, 90.0)
        assert 10_000_000 < dist_equator < 10_020_000

    def test_all_cluster_parcels_within_huntington_beach_envelope(self):
        """Verify all Book 142 parcels fall within Huntington Beach coordinate bounds."""
        for spec in BOOK_142_CLUSTER_SPECS:
            lat = spec["latitude"]
            lon = spec["longitude"]
            assert 33.65 <= lat <= 33.75, f"Latitude out of HB bounds: {lat} for {spec['apn']}"
            assert -118.05 <= lon <= -117.95, f"Longitude out of HB bounds: {lon} for {spec['apn']}"

    def test_all_cluster_parcels_within_radial_proximity(self):
        """All 15 parcels in cluster must be within 0.3 miles of target centroid."""
        target_lat = TARGET_SPEC["latitude"]
        target_lon = TARGET_SPEC["longitude"]
        for spec in BOOK_142_CLUSTER_SPECS:
            dist = haversine_distance_meters(target_lat, target_lon, spec["latitude"], spec["longitude"])
            assert dist <= 482.8, f"Parcel {spec['apn']} at {dist}m exceeds cluster radius bound"


# ==============================================================================
# 3. APN Cadastral Normalization Stress
# ==============================================================================

class TestAdversarialAPNNormalization:
    """Stress tests APN formatting against irregular and adversarial inputs."""

    @pytest.mark.parametrize("raw_input,expected", [
        ("142-073-33", "142-073-33"),
        ("14207333", "142-073-33"),
        ("  142-073-33  ", "142-073-33"),
        ("142 073 33", "142-073-33"),
        ("142.073.33", "142-073-33"),
        ("142/073/33", "142-073-33"),
        ("APN# 14207333", "142-073-33"),
        ("Parcel: 142-073-33", "142-073-33"),
        ("142-075-01", "142-075-01"),
        ("14207501", "142-075-01"),
        ("", ""),
        ("   ", ""),
    ])
    def test_apn_normalization_variants(self, raw_input: str, expected: str):
        normalized = normalize_apn(raw_input)
        assert normalized == expected


# ==============================================================================
# 4. Secret Defense Scanner Penetration Attacks
# ==============================================================================

class TestAdversarialSecretScanner:
    """Simulates credential leaks and validates detection by verify_secret_free.py."""

    def test_gemini_api_key_detected(self):
        # Constructed dynamically without placeholder markers ('dummy', 'fake') so it tests the actual regex
        # Pattern is: \bAIza[0-9A-Za-z\-_]{35}\b -> Total length is 39 characters
        synthetic_key = "AIzaSy" + ("B" * 33)  # 6 + 33 = 39 chars total (4 + 35)
        content = f"production_api_key = '{synthetic_key}'\n"
        violations = scan_text_content(content, "scripts/some_script.py")
        assert len(violations) >= 1
        assert violations[0][1] == "Google / Gemini API Key"

    def test_aws_access_key_detected(self):
        fake_key = "AKIA" + "IOSFODNN7EXAMPLE"
        content = f"AWS_KEY = '{fake_key}'\n"
        violations = scan_text_content(content, "config/aws.py")
        assert len(violations) >= 1
        assert violations[0][1] == "AWS Access Key"

    def test_azure_account_key_detected(self):
        fake_key = "AccountKey=" + ("A" * 86)
        content = f"conn_str = '{fake_key}'\n"
        violations = scan_text_content(content, "deploy/azure.py")
        assert len(violations) >= 1
        assert violations[0][1] == "Azure Connection Key"

    def test_private_key_block_detected(self):
        content = "-----BEGIN RSA " + "PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----\n"
        violations = scan_text_content(content, "keys/id_rsa")
        assert len(violations) >= 1
        assert violations[0][1] == "Private Key Block"

    def test_whitelisted_and_placeholder_markers_ignored(self):
        content = "api_key = 'AIzaSy_REDACTED_PLACEHOLDER_KEY'\n"
        violations = scan_text_content(content, "tests/test_foo.py")
        assert len(violations) == 0

    def test_binary_files_safely_ignored(self):
        assert is_binary_file(Path("scratch/ocgis_map_cameron_radius.png")) is True
        assert is_binary_file(Path("data/test.bak")) is True


# ==============================================================================
# 5. Schema Robustness & Strict Rejection
# ==============================================================================

class TestAdversarialSchemaValidation:
    """Validates that corrupt or non-compliant payloads are strictly rejected."""

    def test_missing_required_parcels_rejected(self):
        sample = {
            "schema_version": "2.0.0",
            "extraction_timestamp": "2026-09-16T22:00:00Z",
            "source_metadata": {
                "portal_url": "https://webapps.ocgis.com/oclandinsights/home/",
                "scraper_engine": "playwright",
                "integrity_hash_algorithm": "sha256"
            },
            "query_parameters": {
                "target_address": "17631 Cameron Ln",
                "spatial_buffer": {
                    "radius_miles": 0.25,
                    "radius_meters": 402.3,
                    "center_coordinates": {
                        "latitude": 33.715,
                        "longitude": -117.989,
                        "spatial_reference": {"wkid": 4326}
                    }
                }
            },
            "summary_statistics": {
                "total_parcels_found": 0,
                "total_permits_found": 0,
                "total_historical_documents": 0,
                "apn_cluster_list": []
            },
            "artifacts": {
                "map_screenshot": {
                    "file_path": "scratch/test.png",
                    "captured_at": "2026-09-16T22:00:00Z",
                    "sha256": "abcdef",
                    "file_size_bytes": 1000,
                    "dimensions": {"width": 1920, "height": 1080}
                }
            }
        }
        is_valid, errors = validate_dataset(sample)
        assert is_valid is False
        assert any("parcels" in err for err in errors)

    def test_invalid_radius_type_rejected(self):
        sample = {
            "schema_version": "2.0.0",
            "extraction_timestamp": "2026-09-16T22:00:00Z",
            "source_metadata": {
                "portal_url": "https://webapps.ocgis.com/oclandinsights/home/",
                "scraper_engine": "playwright",
                "integrity_hash_algorithm": "sha256"
            },
            "query_parameters": {
                "target_address": "17631 Cameron Ln",
                "spatial_buffer": {
                    "radius_miles": "quarter_mile",
                    "radius_meters": 402.3,
                    "center_coordinates": {
                        "latitude": 33.715,
                        "longitude": -117.989,
                        "spatial_reference": {"wkid": 4326}
                    }
                }
            },
            "summary_statistics": {
                "total_parcels_found": 0,
                "total_permits_found": 0,
                "total_historical_documents": 0,
                "apn_cluster_list": []
            },
            "parcels": [],
            "artifacts": {
                "map_screenshot": {
                    "file_path": "scratch/test.png",
                    "captured_at": "2026-09-16T22:00:00Z",
                    "sha256": "abcdef",
                    "file_size_bytes": 1000,
                    "dimensions": {"width": 1920, "height": 1080}
                }
            }
        }
        is_valid, errors = validate_dataset(sample)
        assert is_valid is False
        assert any("radius_miles" in err for err in errors)


# ==============================================================================
# 6. Physical Artifact Empirical Verification
# ==============================================================================

class TestEmpiricalPhysicalArtifacts:
    """Verifies physical deliverables against authoritative thresholds."""

    def test_screenshot_deliverable_physical_metrics(self):
        path = REPO_ROOT / "scratch" / "ocgis_map_cameron_radius.png"
        assert path.exists(), f"Map screenshot does not exist at: {path}"

        size = path.stat().st_size
        assert size > 50_000, f"Map screenshot size {size} bytes is <= 50,000 bytes requirement"

        data = path.read_bytes()
        # Verify PNG Magic Header
        assert data[:8] == b"\x89PNG\r\n\x1a\n", "Corrupted PNG magic signature"

        # Verify IHDR chunk width and height
        assert data[12:16] == b"IHDR", "Missing IHDR chunk in PNG"
        width, height = struct.unpack(">II", data[16:24])
        assert width >= 1920, f"Width {width} is below 1920px minimum"
        assert height >= 1080, f"Height {height} is below 1080px minimum"

    def test_apn_dataset_deliverable_metrics(self):
        path = REPO_ROOT / "data" / "ocgis_historical_apn_data.json"
        assert path.exists(), f"APN dataset does not exist at: {path}"

        size = path.stat().st_size
        assert size > 10_000, f"APN dataset size {size} bytes is suspiciously small"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        is_valid, errors = validate_dataset(data)
        assert is_valid, f"Draft-07 schema errors: {errors}"

        # Check all 15 Book 142 parcels
        parcels = data["parcels"]
        assert len(parcels) == 15, f"Expected 15 parcels, found {len(parcels)}"

        apns = [p["apn"] for p in parcels]
        assert "142-073-33" in apns, "Target APN 142-073-33 missing from cluster"
        assert "142-073-54" in apns, "Adjacent APN 142-073-54 missing"
        assert "142-075-01" in apns, "Shea Homes APN 142-075-01 missing"

        # Check permits on 142-073-33
        target_parcel = next(p for p in parcels if p["apn"] == "142-073-33")
        permits = target_parcel["permits"]
        assert len(permits) >= 5, f"Target parcel has only {len(permits)} permits"
        permit_numbers = [pm["permit_number"] for pm in permits]
        assert "B2020-005995" in permit_numbers, "Building permit B2020-005995 missing"
        assert "CO2020-005184" in permit_numbers, "Certificate of Occupancy CO2020-005184 missing"
        assert "M2020-006464" in permit_numbers, "Mechanical permit M2020-006464 missing"

        # Check empty permit list invariant on unpermitted parcels
        unpermitted = [p for p in parcels if p["apn"] not in ["142-073-33", "142-075-01", "142-075-02"]]
        for p in unpermitted:
            assert p["permits"] == [], f"Parcel {p['apn']} permits must be empty list [], got {p['permits']}"

        # Check screenshot manifest SHA-256 match
        manifest_meta = data["artifacts"]["map_screenshot"]
        screenshot_file = REPO_ROOT / manifest_meta["file_path"]
        assert screenshot_file.exists()
        actual_sha256 = hashlib.sha256(screenshot_file.read_bytes()).hexdigest()
        assert manifest_meta["sha256"] == actual_sha256, (
            f"Manifest SHA256 {manifest_meta['sha256']} does not match actual file SHA256 {actual_sha256}"
        )
        assert manifest_meta["file_size_bytes"] == screenshot_file.stat().st_size
