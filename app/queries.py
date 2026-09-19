import os
import time

BQ_PROJECT = "noble-beanbag-497411-m4"

QUERIES = {
    "edr_summary": {
        "name": "EDR Hits by Type",
        "sql": f"SELECT tags, COUNT(*) as hits, COUNT(DISTINCT source_file) as files FROM `{BQ_PROJECT}.osint_graph.edr_hits` GROUP BY tags ORDER BY hits DESC",
        "description": "Summary of all EDR evidence by tag type"
    },
    "edr_total": {
        "name": "Total EDR Hits",
        "sql": f"SELECT COUNT(*) as total FROM `{BQ_PROJECT}.osint_graph.edr_hits`",
        "description": "Total number of EDR evidence hits"
    },
    "parcels": {
        "name": "All Parcels",
        "sql": f"SELECT apn, target_address, radius FROM `{BQ_PROJECT}.osint_graph.parcels`",
        "description": "All tracked parcel APNs"
    },
    "top_files": {
        "name": "Top EDR File Sources",
        "sql": f"SELECT source_file, COUNT(*) as hits FROM `{BQ_PROJECT}.osint_graph.edr_hits` GROUP BY source_file ORDER BY hits DESC LIMIT 10",
        "description": "Top 10 files with most EDR evidence"
    },
    "keyword_hits": {
        "name": "Keyword Evidence",
        "sql": f"SELECT source_file, context FROM `{BQ_PROJECT}.osint_graph.edr_hits` WHERE tags = 'KEYWORD' LIMIT 10",
        "description": "Evidence matching keyword patterns"
    },
    "year_hits": {
        "name": "Year-Based Evidence",
        "sql": f"SELECT source_file, context FROM `{BQ_PROJECT}.osint_graph.edr_hits` WHERE tags = 'YEAR' LIMIT 10",
        "description": "Evidence matching year patterns"
    },
    "apn_hits": {
        "name": "APN Matches",
        "sql": f"SELECT source_file, context FROM `{BQ_PROJECT}.osint_graph.edr_hits` WHERE tags = 'APN' LIMIT 10",
        "description": "Evidence matching APN patterns"
    },
    "recent_queries": {
        "name": "Recent Query Stats",
        "sql": None,
        "description": "Statistics from local query log"
    },
    "bigquery_info": {
        "name": "BigQuery Dataset Info",
        "sql": f"SELECT COUNT(*) as edr_rows FROM `{BQ_PROJECT}.osint_graph.edr_hits`",
        "description": "BigQuery dataset information"
    }
}

QUICK_COMMANDS = {
    "help": "Available commands: edr, parcels, files, keywords, years, apns, pipeline, status, help",
    "edr": "edr_summary",
    "summary": "edr_summary",
    "parcels": "parcels",
    "parcel": "parcels",
    "files": "top_files",
    "keywords": "keyword_hits",
    "keyword": "keyword_hits",
    "years": "year_hits",
    "year": "year_hits",
    "apns": "apn_hits",
    "apn": "apn_hits",
    "total": "edr_total",
    "info": "bigquery_info",
}

def run_query(sql):
    """Execute a BigQuery query and return results."""
    start = time.time()
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/adc.json"
        from google.cloud import bigquery
        client = bigquery.Client(project=BQ_PROJECT)
        rows = list(client.query(sql).result())
        elapsed_ms = (time.time() - start) * 1000
        result = [dict(r) for r in rows]
        return {
            "success": True,
            "rows": result,
            "count": len(result),
            "elapsed_ms": round(elapsed_ms, 1)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "rows": [], "count": 0}

def format_results(query_name, data):
    """Format query results as readable text."""
    if not data["success"]:
        return f"Query failed: {data['error']}"
    
    rows = data["rows"]
    if not rows:
        return "No results found."
    
    lines = [f"**{QUERIES[query_name]['name']}** ({data['count']} rows, {data['elapsed_ms']}ms)\n"]
    
    for i, row in enumerate(rows[:15]):
        parts = []
        for k, v in row.items():
            if v is not None:
                val = str(v)
                if len(val) > 60:
                    val = val[:60] + "..."
                parts.append(f"{k}: {val}")
        lines.append(f"{i+1}. {' | '.join(parts)}")
    
    if len(rows) > 15:
        lines.append(f"\n... and {len(rows) - 15} more rows")
    
    return "\n".join(lines)
