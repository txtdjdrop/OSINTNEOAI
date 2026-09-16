#!/usr/bin/env python3
"""
scripts/verify_apn_dataset_schema.py
====================================
Draft-07 JSON Schema Validator for OCGIS Historical APN Dataset.
Validates data/ocgis_historical_apn_data.json against authoritative specifications
defined in PROJECT.md and survey_report.3.md.

Usage:
    python scripts/verify_apn_dataset_schema.py [path_to_json]
    python scripts/verify_apn_dataset_schema.py --sample
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    print("Error: 'jsonschema' package is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = REPO_ROOT / "data" / "ocgis_historical_apn_data.json"

DRAFT07_APN_DATASET_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "OCGISHistoricalAPNData",
    "description": "Schema for authoritative APN cluster, spatial attributes, historical permits, and screenshot manifest for Orange County GIS targets.",
    "type": "object",
    "required": [
        "schema_version",
        "extraction_timestamp",
        "source_metadata",
        "query_parameters",
        "summary_statistics",
        "parcels",
        "artifacts"
    ],
    "properties": {
        "schema_version": {
            "type": "string",
            "pattern": r"^[0-9]+\.[0-9]+\.[0-9]+$"
        },
        "extraction_timestamp": {
            "type": "string"
        },
        "source_metadata": {
            "type": "object",
            "required": ["portal_url", "scraper_engine", "integrity_hash_algorithm"],
            "properties": {
                "portal_url": { "type": "string" },
                "viewer_url": { "type": "string" },
                "scraper_engine": { "type": "string" },
                "headless": { "type": "boolean" },
                "integrity_hash_algorithm": { "type": "string", "enum": ["sha256"] },
                "author": { "type": "string" }
            }
        },
        "query_parameters": {
            "type": "object",
            "required": ["target_address", "spatial_buffer"],
            "properties": {
                "target_address": { "type": "string" },
                "target_apn": { "type": ["string", "null"] },
                "spatial_buffer": {
                    "type": "object",
                    "required": ["radius_miles", "radius_meters", "center_coordinates"],
                    "properties": {
                        "radius_miles": { "type": "number", "minimum": 0 },
                        "radius_meters": { "type": "number", "minimum": 0 },
                        "center_coordinates": {
                            "type": "object",
                            "required": ["latitude", "longitude", "spatial_reference"],
                            "properties": {
                                "latitude": { "type": "number" },
                                "longitude": { "type": "number" },
                                "spatial_reference": {
                                    "type": "object",
                                    "properties": {
                                        "wkid": { "type": "integer" },
                                        "latestWkid": { "type": "integer" }
                                    }
                                }
                            }
                        },
                        "buffer_geometry": { "type": "object" }
                    }
                }
            }
        },
        "summary_statistics": {
            "type": "object",
            "required": [
                "total_parcels_found",
                "total_permits_found",
                "total_historical_documents",
                "apn_cluster_list"
            ],
            "properties": {
                "total_parcels_found": { "type": "integer", "minimum": 0 },
                "total_permits_found": { "type": "integer", "minimum": 0 },
                "total_historical_documents": { "type": "integer", "minimum": 0 },
                "apn_cluster_list": {
                    "type": "array",
                    "items": { "type": "string" }
                }
            }
        },
        "parcels": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["apn", "situs_address", "attributes", "permits"],
                "properties": {
                    "apn": {
                        "type": "string"
                    },
                    "apn_raw": { "type": "string" },
                    "situs_address": {
                        "type": "object",
                        "required": ["full_address", "city", "state", "zip_code"],
                        "properties": {
                            "street_number": { "type": ["string", "null"] },
                            "street_name": { "type": ["string", "null"] },
                            "unit": { "type": ["string", "null"] },
                            "city": { "type": "string" },
                            "state": { "type": "string", "maxLength": 2 },
                            "zip_code": { "type": "string" },
                            "full_address": { "type": "string" }
                        }
                    },
                    "owner": {
                        "type": "object",
                        "properties": {
                            "name": { "type": ["string", "null"] },
                            "mailing_address": { "type": ["string", "null"] },
                            "entity_type": { "type": ["string", "null"] }
                        }
                    },
                    "attributes": {
                        "type": "object",
                        "required": ["assessment_no"],
                        "properties": {
                            "assessment_no": { "type": "string" },
                            "legal_description": { "type": ["string", "null"] },
                            "tract_number": { "type": ["string", "null"] },
                            "lot_number": { "type": ["string", "null"] },
                            "use_code": { "type": ["string", "null"] },
                            "use_description": { "type": ["string", "null"] },
                            "zoning": { "type": ["string", "null"] },
                            "acreage": { "type": ["number", "null"] },
                            "lot_sqft": { "type": ["number", "null"] },
                            "year_built": { "type": ["integer", "null"] },
                            "assessed_land_val": { "type": ["number", "null"] },
                            "assessed_improvement_val": { "type": ["number", "null"] }
                        }
                    },
                    "spatial": {
                        "type": "object",
                        "properties": {
                            "centroid": {
                                "type": "object",
                                "properties": {
                                    "latitude": { "type": "number" },
                                    "longitude": { "type": "number" }
                                }
                            },
                            "distance_from_target_meters": { "type": ["number", "null"] }
                        }
                    },
                    "permits": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["permit_number", "permit_type", "status", "filing_date", "description"],
                            "properties": {
                                "permit_number": { "type": "string" },
                                "permit_type": { "type": "string" },
                                "status": { "type": "string" },
                                "filing_date": { "type": "string" },
                                "issue_date": { "type": ["string", "null"] },
                                "final_date": { "type": ["string", "null"] },
                                "description": { "type": "string" },
                                "contractor": { "type": ["string", "null"] },
                                "source": { "type": "string" }
                            }
                        }
                    },
                    "historical_documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "document_id": { "type": "string" },
                                "document_type": { "type": "string" },
                                "recording_date": { "type": ["string", "null"] },
                                "url": { "type": ["string", "null"] }
                            }
                        }
                    }
                }
            }
        },
        "spatial_layers": {
            "type": "object",
            "properties": {
                "centerlines": { "type": "array" },
                "records_of_survey": { "type": "array" },
                "tentative_maps": { "type": "array" }
            }
        },
        "artifacts": {
            "type": "object",
            "required": ["map_screenshot"],
            "properties": {
                "map_screenshot": {
                    "type": "object",
                    "required": ["file_path", "captured_at", "sha256", "dimensions"],
                    "properties": {
                        "file_path": { "type": "string" },
                        "captured_at": { "type": "string" },
                        "sha256": { "type": "string", "pattern": r"^[a-f0-9]{64}$" },
                        "file_size_bytes": { "type": "integer" },
                        "dimensions": {
                            "type": "object",
                            "properties": {
                                "width": { "type": "integer" },
                                "height": { "type": "integer" },
                                "device_scale_factor": { "type": "number" }
                            }
                        }
                    }
                },
                "auxiliary_screenshots": {
                    "type": "array",
                    "items": { "type": "string" }
                }
            }
        }
    }
}


def get_canonical_sample_payload() -> Dict[str, Any]:
    """Return an authoritative valid sample APN dataset payload."""
    return {
        "schema_version": "2.0.0",
        "extraction_timestamp": "2026-09-16T18:30:00Z",
        "source_metadata": {
            "portal_url": "https://webapps.ocgis.com/oclandinsights/home/",
            "viewer_url": "https://webapps.ocgis.com/oclandinsights/map-viewer?id=2",
            "scraper_engine": "playwright_esri_v2",
            "headless": True,
            "integrity_hash_algorithm": "sha256",
            "author": "OsintNeoAi Autonomous GIS Engine"
        },
        "query_parameters": {
            "target_address": "17631 Cameron Ln, Huntington Beach, CA 92647",
            "target_apn": "142-073-33",
            "spatial_buffer": {
                "radius_miles": 0.25,
                "radius_meters": 402.336,
                "center_coordinates": {
                    "latitude": 33.715362,
                    "longitude": -117.989211,
                    "spatial_reference": {
                        "wkid": 4326,
                        "latestWkid": 4326
                    }
                }
            }
        },
        "summary_statistics": {
            "total_parcels_found": 15,
            "total_permits_found": 3,
            "total_historical_documents": 1,
            "apn_cluster_list": [
                "142-073-33", "142-073-54", "142-075-01", "142-075-02",
                "142-082-35", "142-122-07", "142-242-16", "142-253-04",
                "142-321-20", "142-492-11", "142-056-53", "142-063-04",
                "142-160-29", "142-207-90", "142-356-93"
            ]
        },
        "parcels": [
            {
                "apn": "142-073-33",
                "apn_raw": "14207333",
                "situs_address": {
                    "street_number": "17631",
                    "street_name": "Cameron Ln",
                    "unit": None,
                    "city": "Huntington Beach",
                    "state": "CA",
                    "zip_code": "92647",
                    "full_address": "17631 Cameron Ln, Huntington Beach, CA 92647"
                },
                "owner": {
                    "name": "CITY OF HUNTINGTON BEACH / PUBLIC USE",
                    "mailing_address": "2000 Main St, Huntington Beach, CA 92648",
                    "entity_type": "Municipal"
                },
                "attributes": {
                    "assessment_no": "142-073-33",
                    "legal_description": "TRACT 142 LOT 33 EX OF ST",
                    "tract_number": "142",
                    "lot_number": "33",
                    "use_code": "8200",
                    "use_description": "Commercial / Municipal Navigation Center",
                    "zoning": "SP-14 (Beach & Edinger Corridors Specific Plan)",
                    "acreage": 0.84,
                    "lot_sqft": 36590.4,
                    "year_built": 2020,
                    "assessed_land_val": 1850000.0,
                    "assessed_improvement_val": 920000.0
                },
                "spatial": {
                    "centroid": {
                        "latitude": 33.715362,
                        "longitude": -117.989211
                    },
                    "distance_from_target_meters": 0.0
                },
                "permits": [
                    {
                        "permit_number": "B2020-005995",
                        "permit_type": "Commercial and Industrial Building",
                        "status": "Pending (Pay Fees Due)",
                        "filing_date": "2020-10-19",
                        "issue_date": None,
                        "final_date": None,
                        "description": "SHELL - OFFICE TRAILER 1-4 - FOUNDATION ANCHORAGE & STAIRS/RAMPS **** NAVIGATION CENTER - MERCY HOUSE **** PURSUANT TO RESOLUTION 2019-22",
                        "contractor": "Mercy House / woom",
                        "source": "City of Huntington Beach Accela"
                    },
                    {
                        "permit_number": "CO2020-005184",
                        "permit_type": "Certificate of Occupancy",
                        "status": "Issued",
                        "filing_date": "2020-09-11",
                        "issue_date": "2020-09-11",
                        "final_date": None,
                        "description": "SHELL ONLY - SPRUNG STRUCTURE BUILDING (DORMITORY) FOR EMERGENCY HOMELESS SHELTER **** NAVIGATION CENTER - MERCY HOUSE **** PURSUANT TO RESOLUTION 2019-22",
                        "contractor": "Mercy House / kongs",
                        "source": "City of Huntington Beach Accela"
                    },
                    {
                        "permit_number": "M2020-006464",
                        "permit_type": "Commercial and Industrial Mechanical",
                        "status": "Finaled",
                        "filing_date": "2020-11-06",
                        "issue_date": "2020-11-06",
                        "final_date": "2020-11-20",
                        "description": "MDMECH TO PROVIDE HVAC FOR TRAILERS ***** MERCY HOUSE ***** PURSUANT TO RESOLUTION 2019-22",
                        "contractor": "MDMECH / woom",
                        "source": "City of Huntington Beach Accela"
                    }
                ],
                "historical_documents": [
                    {
                        "document_id": "TM-10-142",
                        "document_type": "Tentative Map",
                        "recording_date": "1968-04-12",
                        "url": "https://www.ocgis.com/survey/rest/services/Landbase/TentativeMaps/FeatureServer/10/query"
                    }
                ]
            }
        ],
        "spatial_layers": {
            "centerlines": ["Cameron Ln", "Beach Blvd", "Slater Ave"],
            "records_of_survey": [],
            "tentative_maps": ["TM-10-142"]
        },
        "artifacts": {
            "map_screenshot": {
                "file_path": "scratch/ocgis_map_cameron_radius.png",
                "captured_at": "2026-09-16T18:30:15Z",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "file_size_bytes": 1420512,
                "dimensions": {
                    "width": 1920,
                    "height": 1080,
                    "device_scale_factor": 2.0
                }
            },
            "auxiliary_screenshots": [
                "scratch/ocgis_cameron_parcels_active.png"
            ]
        }
    }


def validate_dataset(data: Any) -> Tuple[bool, List[str]]:
    """
    Validate an in-memory python dictionary against the Draft-07 APN dataset schema.
    Returns:
        (is_valid, list_of_error_messages)
    """
    validator = Draft7Validator(DRAFT07_APN_DATASET_SCHEMA)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if not errors:
        return True, []
    
    error_messages = []
    for err in errors:
        path = " -> ".join([str(p) for p in err.absolute_path]) or "root"
        error_messages.append(f"[{path}] {err.message}")
    return False, error_messages


def validate_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Read and validate a JSON file against the Draft-07 APN dataset schema.
    Returns:
        (is_valid, list_of_error_messages)
    """
    path = Path(file_path)
    if not path.exists():
        return False, [f"File not found: {path}"]
    
    try:
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        return False, [f"Malformed JSON in {path}: {exc}"]
    except Exception as exc:
        return False, [f"Error reading {path}: {exc}"]
    
    return validate_dataset(data)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        sample = get_canonical_sample_payload()
        is_valid, errors = validate_dataset(sample)
        if is_valid:
            print("✅ CANONICAL SAMPLE VALIDATION SUCCESS: Conforms 100% to Draft-07 Schema.")
            sys.exit(0)
        else:
            print("❌ CANONICAL SAMPLE VALIDATION FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)

    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_PATH
    print(f"🔍 Validating APN dataset schema for: {target_path}")
    
    is_valid, errors = validate_file(target_path)
    if is_valid:
        print(f"✅ SCHEMA VALIDATION SUCCESS: '{target_path.name}' conforms 100% to Draft-07 Schema.")
        sys.exit(0)
    else:
        print(f"❌ SCHEMA VALIDATION FAILED: {len(errors)} violation(s) detected in '{target_path.name}':", file=sys.stderr)
        for idx, err in enumerate(errors, start=1):
            print(f"  {idx}. {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
