import os
import time
import json
from datetime import datetime

BQ_PROJECT = "noble-beanbag-497411-m4"

def get_token():
    import subprocess
    result = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    return result.stdout.strip()

def run_bigquery(sql):
    import requests
    token = get_token()
    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{BQ_PROJECT}/queries"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"query": sql, "useLegacySql": False}
    r = requests.post(url, headers=headers, json=body)
    if r.status_code != 200:
        return []
    data = r.json()
    if "rows" in data:
        schema = [f["name"] for f in data.get("schema", {}).get("fields", [])]
        return [dict(zip(schema, [cell.get("v") for cell in row["f"]])) for row in data["rows"]]
    return []

PHASES = [
    {
        "name": "Evidence Inventory",
        "description": "Count and categorize all EDR evidence",
        "query": f"SELECT tags, COUNT(*) as hits FROM `{BQ_PROJECT}.osint_graph.edr_hits` GROUP BY tags ORDER BY hits DESC"
    },
    {
        "name": "Parcel Graph",
        "description": "Map tracked parcels and properties",
        "query": f"SELECT apn, target_address, radius FROM `{BQ_PROJECT}.osint_graph.parcels`"
    },
    {
        "name": "EDR Cross-Reference",
        "description": "Identify files with most evidence",
        "query": f"SELECT source_file, COUNT(*) as hits FROM `{BQ_PROJECT}.osint_graph.edr_hits` GROUP BY source_file ORDER BY hits DESC LIMIT 15"
    },
    {
        "name": "Temporal Analysis",
        "description": "Analyze evidence by creation date",
        "query": f"SELECT DATE(created_at) as day, COUNT(*) as hits FROM `{BQ_PROJECT}.osint_graph.edr_hits` GROUP BY day ORDER BY day"
    },
    {
        "name": "Entity Extraction",
        "description": "Extract entities from evidence context",
        "query": f"SELECT tags, context FROM `{BQ_PROJECT}.osint_graph.edr_hits` WHERE tags = 'KEYWORD' LIMIT 5"
    },
    {
        "name": "GIS Spatial",
        "description": "GIS data status (stored compressed)",
        "query": None
    },
    {
        "name": "Forensic Report",
        "description": "Generate final summary",
        "query": f"SELECT (SELECT COUNT(*) FROM `{BQ_PROJECT}.osint_graph.edr_hits`) as edr, (SELECT COUNT(*) FROM `{BQ_PROJECT}.osint_graph.parcels`) as parcels"
    }
]

def run_pipeline(phase=None):
    """Run the full pipeline or a specific phase."""
    results = []
    start_time = time.time()
    
    if phase is not None:
        phases_to_run = [PHASES[phase]] if phase < len(PHASES) else []
    else:
        phases_to_run = PHASES
    
    for i, p in enumerate(PHASES if phase is None else phases_to_run):
        phase_num = i if phase is None else phase
        phase_start = time.time()
        result = {"phase": phase_num + 1, "name": p["name"], "status": "running"}
        
        if p["query"]:
            try:
                data = run_bigquery(p["query"])
                result["rows"] = data
                result["count"] = len(data)
                result["status"] = "complete"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
        else:
            result["status"] = "complete"
            result["note"] = "GIS data stored on Google Drive (53MB compressed)"
        
        result["elapsed_ms"] = round((time.time() - phase_start) * 1000, 1)
        results.append(result)
    
    total_ms = round((time.time() - start_time) * 1000, 1)
    return {
        "phases": results,
        "total_ms": total_ms,
        "timestamp": datetime.now().isoformat()
    }

def format_pipeline_result(result):
    """Format pipeline result as readable text."""
    lines = [f"**7-PHASE FORENSIC PIPELINE**\nTimestamp: {result['timestamp']}\n"]
    
    for phase in result["phases"]:
        status_icon = "+" if phase["status"] == "complete" else "!"
        lines.append(f"Phase {phase['phase']}: [{status_icon}] {phase['name']}")
        
        if phase["status"] == "complete":
            if "count" in phase:
                lines.append(f"  {phase['count']} rows returned")
            elif "note" in phase:
                lines.append(f"  {phase['note']}")
        elif phase["status"] == "error":
            lines.append(f"  Error: {phase.get('error', 'unknown')}")
    
    lines.append(f"\nTotal: {result['total_ms']}ms")
    return "\n".join(lines)
