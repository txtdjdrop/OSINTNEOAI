"""Load OSINT data into BigQuery for Gemini chat integration"""
from google.cloud import bigquery
import json
from pathlib import Path

# Initialize client
client = bigquery.Client(project="blah-905ad")

# Load breach data
print("Loading breach data...")
breach_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/huntington_beach/breach_check_results.json")
with open(breach_path) as f:
    breach_data = json.load(f)

breach_rows = []
for email, data in breach_data["emails"].items():
    sources = ", ".join([s["name"] for s in data.get("sources", [])])
    risk = "CRITICAL" if data.get("status") == "COMPROMISED" and data.get("found", 0) >= 5 else \
           "HIGH" if data.get("status") == "COMPROMISED" else "NONE"
    breach_rows.append({
        "email": email,
        "status": data.get("status", ""),
        "breaches": data.get("found", 0),
        "sources": sources,
        "risk_level": risk,
        "scan_date": breach_data["timestamp"]
    })

# Insert breach data
table_id = "blah-905ad.osint_investigation.breach_results"
errors = client.insert_rows_json(table_id, breach_rows)
if errors:
    print(f"Breach load errors: {errors}")
else:
    print(f"Loaded {len(breach_rows)} breach records")

# Load grants data
print("\nLoading grants data...")
grants_path = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/taxfunded_grants_ingestion.json")
with open(grants_path) as f:
    grants_data = json.load(f)

grant_rows = []
for g in grants_data.get("grants", []):
    grant_rows.append({
        "award_id": g.get("award_id", ""),
        "funding_agency": g.get("funding_agency", ""),
        "recipient_name": g.get("recipient_name", ""),
        "amount_usd": g.get("amount_usd", 0),
        "purpose": g.get("purpose", ""),
        "city": g.get("city", ""),
        "state": g.get("state", ""),
        "status": g.get("status", ""),
        "utxo_tags": ", ".join(g.get("utxo_tag", [])),
        "source_api": g.get("source_api", ""),
        "sha256_hash": g.get("sha256_hash", ""),
        "ingested_at": g.get("ingested_at", "")
    })

table_id = "blah-905ad.osint_investigation.grants_tracked"
errors = client.insert_rows_json(table_id, grant_rows)
if errors:
    print(f"Grants load errors: {errors}")
else:
    print(f"Loaded {len(grant_rows)} grant records")

# Load HBNC entities
print("\nLoading HBNC entities...")
entities = [
    {"entity_name": "Mercy House Living Centers", "entity_type": "Operator", "email": "", "phone": "", "address": "17642 Beach Blvd", "role": "Shelter Operator", "organization": "Mercy House", "notes": "174-bed emergency shelter"},
    {"entity_name": "TTS Engineering", "entity_type": "Contractor", "email": "info@ttsengineering.net", "phone": "", "address": "", "role": "Engineering/Design", "organization": "TTS Engineering", "notes": "SCE relationship, underground vaults"},
    {"entity_name": "RPM Team", "entity_type": "Contractor", "email": "contact@rpm-team.com", "phone": "", "address": "", "role": "Design/PM", "organization": "RPM Team", "notes": "Project management"},
    {"entity_name": "EEC Environmental", "entity_type": "Contractor", "email": "info@eecenvironmental.com", "phone": "", "address": "", "role": "Environmental Oversight", "organization": "EEC Environmental", "notes": "File #20-9204"},
    {"entity_name": "City of Huntington Beach", "entity_type": "Government", "email": "", "phone": "", "address": "", "role": "Funder", "organization": "City of HB", "notes": "$8.2M+ investment"},
    {"entity_name": "SCE (Southern California Edison)", "entity_type": "Utility", "email": "", "phone": "", "address": "", "role": "Utility Provider", "organization": "SCE", "notes": "12kV primary underground, 1970 easement"},
    {"entity_name": "Julie Toledo", "entity_type": "Individual", "email": "julie.toledo@surfcity-hb.org", "phone": "", "address": "", "role": "City Staff", "organization": "City of HB", "notes": "5 breaches - CRITICAL"},
    {"entity_name": "Alejandro Pinel", "entity_type": "Individual", "email": "", "phone": "", "address": "", "role": "Construction Manager", "organization": "City of HB", "notes": "HBNC construction"},
]

table_id = "blah-905ad.osint_investigation.hbnc_entities"
errors = client.insert_rows_json(table_id, entities)
if errors:
    print(f"Entities load errors: {errors}")
else:
    print(f"Loaded {len(entities)} entity records")

print("\nAll data loaded to BigQuery!")
print(f"Dataset: blah-905ad:osint_investigation")
print(f"Tables: breach_results, grants_tracked, hbnc_entities")
