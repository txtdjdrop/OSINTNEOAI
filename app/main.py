import os
import sys
import json
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.chat import init_db, save_message, get_history, save_query, get_query_stats
from app.queries import QUERIES, QUICK_COMMANDS, run_query, format_results
from app.pipeline import run_pipeline, format_pipeline_result

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.urandom(24)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/adc.json"

init_db()

@app.route("/")
def index():
    stats = get_query_stats()
    return render_template("index.html", stats=stats)

@app.route("/chat")
def chat_page():
    history = get_history(50)
    return render_template("chat.html", history=history)

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/pipeline")
def pipeline_page():
    return render_template("pipeline.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"error": "Empty message"}), 400
    
    save_message("user", message)
    
    response = process_chat(message)
    
    save_message("assistant", response, {"message": message})
    
    return jsonify({"response": response, "timestamp": datetime.now().isoformat()})

def process_chat(message):
    """Process a chat message and return a response."""
    lower = message.lower().strip()
    
    if lower in ("help", "?", "commands"):
        return ("**Available Commands:**\n\n"
                "- **edr** / **summary** — EDR hits by type\n"
                "- **parcels** — All tracked parcels\n"
                "- **files** — Top evidence files\n"
                "- **keywords** — Keyword evidence\n"
                "- **years** — Year-based evidence\n"
                "- **apns** — APN matches\n"
                "- **total** — Total hit count\n"
                "- **pipeline** — Run 7-phase pipeline\n"
                "- **status** — System status\n"
                "- **help** — This message\n\n"
                "Or ask naturally: \"show me EDR hits\" / \"run pipeline\"")
    
    if lower in ("status", "sys", "system"):
        try:
            uptime = subprocess.run(["uptime", "-p"], capture_output=True, text=True).stdout.strip()
            mem = subprocess.run(["free", "-h", "--total", "-w"], capture_output=True, text=True).stdout
            disk = subprocess.run(["df", "-h", "/"], capture_output=True, text=True).stdout
            return f"**System Status**\n\n{uptime}\n\n```\n{mem}\n{disk}\n```"
        except:
            return "System status unavailable."
    
    if lower in ("pipeline", "run pipeline", "full pipeline"):
        result = run_pipeline()
        return format_pipeline_result(result)
    
    if lower.startswith("pipeline "):
        try:
            phase_num = int(lower.split()[-1]) - 1
            if 0 <= phase_num < 7:
                result = run_pipeline(phase=phase_num)
                return format_pipeline_result(result)
            return f"Invalid phase number. Use 1-7."
        except ValueError:
            return "Usage: pipeline <phase_number> (1-7)"
    
    if lower.startswith("run edr") or lower.startswith("edr scan"):
        try:
            result = subprocess.run(
                ["python3", "tools/edr_historical_scraper.py"],
                capture_output=True, text=True, timeout=120,
                cwd="/home/brainmedus_gmail_com/OsintNeoAi"
            )
            output = result.stdout[-500:] if result.stdout else result.stderr[-500:]
            return f"**EDR Scan Complete**\n\n```\n{output}\n```"
        except Exception as e:
            return f"EDR scan failed: {e}"
    
    if lower.startswith("run ocgis") or lower.startswith("ocgis"):
        try:
            result = subprocess.run(
                ["python3", "tools/ocgis_scraper.py"],
                capture_output=True, text=True, timeout=120,
                cwd="/home/brainmedus_gmail_com/OsintNeoAi"
            )
            output = result.stdout[-500:] if result.stdout else result.stderr[-500:]
            return f"**OCGIS Scrape Complete**\n\n```\n{output}\n```"
        except Exception as e:
            return f"OCGIS scrape failed: {e}"
    
    if lower in QUICK_COMMANDS:
        query_name = QUICK_COMMANDS[lower]
        if query_name in QUERIES and QUERIES[query_name]["sql"]:
            data = run_query(QUERIES[query_name]["sql"])
            save_query(QUERIES[query_name]["sql"], data["count"], data.get("elapsed_ms", 0))
            return format_results(query_name, data)
    
    for keyword, query_name in QUICK_COMMANDS.items():
        if keyword in lower and query_name in QUERIES and QUERIES[query_name]["sql"]:
            data = run_query(QUERIES[query_name]["sql"])
            save_query(QUERIES[query_name]["sql"], data["count"], data.get("elapsed_ms", 0))
            return format_results(query_name, data)
    
    if "show" in lower or "get" in lower or "list" in lower or "find" in lower:
        for keyword, query_name in QUICK_COMMANDS.items():
            if keyword in lower and query_name in QUERIES and QUERIES[query_name]["sql"]:
                data = run_query(QUERIES[query_name]["sql"])
                save_query(QUERIES[query_name]["sql"], data["count"], data.get("elapsed_ms", 0))
                return format_results(query_name, data)
    
    if lower.startswith("sql ") or lower.startswith("query "):
        sql = message[4:] if lower.startswith("sql ") else message[6:]
        data = run_query(sql)
        if data["success"]:
            return f"**Query Results** ({data['count']} rows, {data['elapsed_ms']}ms)\n\n" + "\n".join(
                [f"{i+1}. {json.dumps(row, default=str)}" for i, row in enumerate(data["rows"][:10])]
            )
        return f"Query error: {data['error']}"
    
    return (f"I don't understand \"{message}\".\n\n"
            "Try: **edr**, **parcels**, **files**, **pipeline**, **status**, **help**\n\n"
            "Or ask: \"show EDR hits\", \"run pipeline\", \"query SELECT * FROM table\"")

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.get_json()
    query_name = data.get("query", "")
    sql = data.get("sql", "")
    
    if sql:
        result = run_query(sql)
        save_query(sql, result["count"], result.get("elapsed_ms", 0))
        return jsonify(result)
    
    if query_name in QUERIES and QUERIES[query_name]["sql"]:
        result = run_query(QUERIES[query_name]["sql"])
        save_query(QUERIES[query_name]["sql"], result["count"], result.get("elapsed_ms", 0))
        return jsonify(result)
    
    return jsonify({"error": "Unknown query"}), 400

@app.route("/api/queries")
def api_queries():
    return jsonify({"queries": {k: {"name": v["name"], "description": v["description"]} for k, v in QUERIES.items()}})

@app.route("/api/pipeline/run", methods=["POST"])
def api_pipeline_run():
    data = request.get_json() or {}
    phase = data.get("phase")
    result = run_pipeline(phase=phase)
    return jsonify(result)

@app.route("/api/stats")
def api_stats():
    stats = get_query_stats()
    return jsonify(stats)

@app.route("/api/logs")
def api_logs():
    try:
        result = subprocess.run(
            ["journalctl", "-u", "osintneoai", "--no-pager", "-n", "50"],
            capture_output=True, text=True, timeout=10
        )
        return jsonify({"logs": result.stdout})
    except:
        return jsonify({"logs": "Logs unavailable"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
