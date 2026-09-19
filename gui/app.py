#!/usr/bin/env python3
"""OSINT Neo AI - Web GUI"""
import os
import json
import subprocess
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>OSINT Neo AI</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#0a0a0a; color:#00ff41; }
.header { background:#111; padding:20px; border-bottom:2px solid #00ff41; }
.header h1 { font-size:28px; }
.header p { color:#888; }
.container { display:grid; grid-template-columns:250px 1fr; min-height:90vh; }
.sidebar { background:#111; padding:20px; border-right:1px solid #333; }
.sidebar h3 { color:#00ff41; margin:15px 0 10px; font-size:14px; }
.sidebar a { display:block; color:#aaa; text-decoration:none; padding:8px 12px; border-radius:4px; margin:2px 0; }
.sidebar a:hover { background:#1a1a1a; color:#00ff41; }
.sidebar a.active { background:#00ff41; color:#000; }
.main { padding:20px; }
.tool-card { background:#111; border:1px solid #333; border-radius:8px; padding:20px; margin:10px 0; }
.tool-card h2 { color:#00ff41; margin-bottom:10px; }
.tool-card p { color:#888; margin-bottom:15px; }
.btn { background:#00ff41; color:#000; border:none; padding:10px 20px; border-radius:4px; cursor:pointer; font-weight:bold; }
.btn:hover { background:#00cc33; }
.input-group { margin:10px 0; }
.input-group label { display:block; color:#888; margin-bottom:5px; }
.input-group input, .input-group select, .input-group textarea {
  width:100%; padding:10px; background:#1a1a1a; border:1px solid #333;
  color:#00ff41; border-radius:4px; font-family:monospace;
}
.output { background:#000; border:1px solid #333; border-radius:4px; padding:15px; margin-top:15px; font-family:monospace; max-height:400px; overflow-y:auto; white-space:pre-wrap; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:15px; }
.status { display:inline-block; width:8px; height:8px; border-radius:50%; background:#00ff41; margin-right:5px; }
</style>
</head>
<body>
<div class="header">
<h1>&#9760; OSINT Neo AI</h1>
<p>Open Source Intelligence Platform | Free Tier Active | Budget: $5</p>
</div>
<div class="container">
<div class="sidebar">
<h3>DASHBOARDS</h3>
<a href="/" class="active">Home</a>
<a href="/gis">GIS Maps</a>
<a href="/huntington">HBNC Investigation</a>
<h3>OSINT TOOLS</h3>
<a href="/email">Email Recon</a>
<a href="/domain">Domain Recon</a>
<a href="/breach">Breach Check</a>
<a href="/phone">Phone Lookup</a>
<a href="/address">Address Search</a>
<h3>INTELLIGENCE</h3>
<a href="/newspaper">Newspaper</a>
<a href="/legal">Legal Section</a>
<a href="/txf">TXF Ledger</a>
<h3>DATA</h3>
<a href="/bigquery">BigQuery</a>
<a href="/arcgis">ArcGIS Hub</a>
<a href="/parcels">Parcel Data</a>
<h3>SYSTEM</h3>
<a href="/status">System Status</a>
</div>
<div class="main">
{{ content|safe }}
</div>
</div>
</body>
</html>
"""

HOME = """
<div class="grid">
<div class="tool-card">
<h2>&#128269; Email Recon</h2>
<p>Check email accounts, breaches, social media</p>
<a href="/email" class="btn">Open Tool</a>
</div>
<div class="tool-card">
<h2>&#127760; Domain Recon</h2>
<p>DNS, WHOIS, subdomains, tech stack</p>
<a href="/domain" class="btn">Open Tool</a>
</div>
<div class="tool-card">
<h2>&#128274; Breach Check</h2>
<p>Check if emails/passwords were leaked</p>
<a href="/breach" class="btn">Open Tool</a>
</div>
<div class="tool-card">
<h2>&#128205; GIS Maps</h2>
<p>ArcGIS, parcels, zoning, infrastructure</p>
<a href="/gis" class="btn">Open Tool</a>
</div>
<div class="tool-card">
<h2>&#127970; HBNC Investigation</h2>
<p>Huntington Beach Navigation Center data</p>
<a href="/huntington" class="btn">Open Tool</a>
</div>
<div class="tool-card">
<h2>&#128270; Phone Lookup</h2>
<p>Reverse phone, carrier, location</p>
<a href="/phone" class="btn">Open Tool</a>
</div>
</div>
"""

EMAIL_TOOL = """
<div class="tool-card">
<h2>&#128269; Email Reconnaissance</h2>
<div class="input-group">
<label>Email Address</label>
<input type="text" id="email" placeholder="target@example.com">
</div>
<button class="btn" onclick="scanEmail()">Scan Email</button>
<div class="output" id="result">Ready to scan...</div>
</div>
<script>
async function scanEmail() {
  const email = document.getElementById('email').value;
  const out = document.getElementById('result');
  out.textContent = 'Scanning ' + email + '...';
  try {
    const r = await fetch('/api/email?email=' + encodeURIComponent(email));
    const d = await r.json();
    out.textContent = JSON.stringify(d, null, 2);
  } catch(e) { out.textContent = 'Error: ' + e; }
}
</script>
"""

DOMAIN_TOOL = """
<div class="tool-card">
<h2>&#127760; Domain Reconnaissance</h2>
<div class="input-group">
<label>Domain</label>
<input type="text" id="domain" placeholder="example.com">
</div>
<button class="btn" onclick="scanDomain()">Scan Domain</button>
<div class="output" id="result">Ready to scan...</div>
</div>
<script>
async function scanDomain() {
  const domain = document.getElementById('domain').value;
  const out = document.getElementById('result');
  out.textContent = 'Scanning ' + domain + '...';
  try {
    const r = await fetch('/api/domain?domain=' + encodeURIComponent(domain));
    const d = await r.json();
    out.textContent = JSON.stringify(d, null, 2);
  } catch(e) { out.textContent = 'Error: ' + e; }
}
</script>
"""

GIS_TOOL = """
<div class="tool-card">
<h2>&#128205; GIS Data Explorer</h2>
<div class="input-group">
<label>Dataset</label>
<select id="dataset">
<option value="parcels">HB Parcels (50K)</option>
<option value="tracts">HB Tracts</option>
<option value="zoning">HB Zoning</option>
<option value="subsidence">Subsidence Zones</option>
<option value="streets">Street Centers</option>
<option value="cip">CIP Projects</option>
<option value="oil">Oil Wells</option>
<option value="flood">FEMA Flood Zones</option>
</select>
</div>
<button class="btn" onclick="loadGIS()">Load Data</button>
<div class="output" id="result">Select dataset and click Load...</div>
</div>
<script>
async function loadGIS() {
  const ds = document.getElementById('dataset').value;
  const out = document.getElementById('result');
  out.textContent = 'Loading ' + ds + '...';
  try {
    const r = await fetch('/api/gis?dataset=' + ds);
    const d = await r.json();
    out.textContent = 'Records: ' + d.count + '\\n' + JSON.stringify(d.sample, null, 2);
  } catch(e) { out.textContent = 'Error: ' + e; }
}
</script>
"""

@app.route("/")
def home():
    return render_template_string(HTML, content=HOME)

@app.route("/email")
def email_page():
    return render_template_string(HTML, content=EMAIL_TOOL)

@app.route("/domain")
def domain_page():
    return render_template_string(HTML, content=DOMAIN_TOOL)

@app.route("/gis")
def gis_page():
    return render_template_string(HTML, content=GIS_TOOL)

@app.route("/huntington")
def huntington_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>HBNC Investigation</h2><p>Loading...</p></div>")

@app.route("/breach")
def breach_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>Breach Check</h2><p>Coming soon...</p></div>")

@app.route("/phone")
def phone_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>Phone Lookup</h2><p>Coming soon...</p></div>")

@app.route("/address")
def address_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>Address Search</h2><p>Coming soon...</p></div>")

@app.route("/bigquery")
def bigquery_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>BigQuery</h2><p>Coming soon...</p></div>")

@app.route("/arcgis")
def arcgis_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>ArcGIS Hub</h2><p>Coming soon...</p></div>")

@app.route("/parcels")
def parcels_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>Parcel Data</h2><p>Coming soon...</p></div>")

@app.route("/newspaper")
def newspaper_page():
    try:
        from newspaper import generate
        data = generate()
        content = f"""
<div class="tool-card">
<h2>&#128240; OSINT Intelligence Newspaper</h2>
<p>Self-populating newspaper from all investigation data</p>
<div class="grid">
<div class="tool-card">
<h3>Articles: {data['total_articles']}</h3>
<p>Auto-generated from OSINT data files</p>
</div>
<div class="tool-card">
<h3>Hyperlinks: {data['stats']['total_hyperlinks']}</h3>
<p>Cross-referenced sources</p>
</div>
<div class="tool-card">
<h3>Tags: {data['stats']['total_tags']}</h3>
<p>Extracted intelligence topics</p>
</div>
</div>
<a href="/newspaper/view" class="btn">View Newspaper</a>
</div>
"""
        return render_template_string(HTML, content=content)
    except Exception as e:
        return render_template_string(HTML, content=f"<div class='tool-card'><h2>Error</h2><p>{str(e)}</p></div>")

@app.route("/newspaper/view")
def newspaper_view():
    try:
        from pathlib import Path
        html_path = Path.home() / "OsintNeoAi" / "data" / "ledger" / "newspaper.html"
        if html_path.exists():
            return html_path.read_text()
        return "Newspaper not generated yet. Visit /newspaper first."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/legal")
def legal_page():
    try:
        from legal import generate
        data = generate()
        content = f"""
<div class="tool-card">
<h2>&#9878; Legal Section</h2>
<p>Growing database of legal documents with hyperlinks</p>
<div class="grid">
<div class="tool-card">
<h3>Documents: {data['total_documents']}</h3>
<p>Permits, contracts, complaints, ordinances</p>
</div>
<div class="tool-card">
<h3>Categories: {len(data['categories'])}</h3>
<p>Auto-classified legal document types</p>
</div>
<div class="tool-card">
<h3>Hyperlinks: {len(data['hyperlink_index'])}</h3>
<p>Linked to official records</p>
</div>
</div>
<a href="/legal/view" class="btn">View Legal Index</a>
</div>
"""
        return render_template_string(HTML, content=content)
    except Exception as e:
        return render_template_string(HTML, content=f"<div class='tool-card'><h2>Error</h2><p>{str(e)}</p></div>")

@app.route("/legal/view")
def legal_view():
    try:
        from pathlib import Path
        html_path = Path.home() / "OsintNeoAi" / "data" / "legal" / "legal_index.html"
        if html_path.exists():
            return html_path.read_text()
        return "Legal index not generated yet. Visit /legal first."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/txf")
def txf_page():
    try:
        from txf_token import load_or_init_ledger
        data = load_or_init_ledger()
        content = f"""
<div class="tool-card">
<h2>&#127981; TXF Token Ledger</h2>
<p>Taxpayer OSINT on the ledger | Every query tracked</p>
<div class="grid">
<div class="tool-card">
<h3>Blocks: {data['stats']['total_blocks']}</h3>
<p>Blockchain-verified entries</p>
</div>
<div class="tool-card">
<h3>Transactions: {data['stats']['total_transactions']}</h3>
<p>OSINT queries, data access, funds</p>
</div>
<div class="tool-card">
<h3>Supply: {data['stats']['total_supply']} TXF</h3>
<p>Total token supply</p>
</div>
</div>
<a href="/txf/view" class="btn">View Ledger</a>
</div>
"""
        return render_template_string(HTML, content=content)
    except Exception as e:
        return render_template_string(HTML, content=f"<div class='tool-card'><h2>Error</h2><p>{str(e)}</p></div>")

@app.route("/txf/view")
def txf_view():
    try:
        from pathlib import Path
        html_path = Path.home() / "OsintNeoAi" / "data" / "ledger" / "txf_ledger.html"
        if html_path.exists():
            return html_path.read_text()
        return "TXF ledger not initialized yet. Visit /txf first."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/txf/log", methods=["POST"])
def txf_log():
    try:
        from txf_token import TXFToken
        data = request.json
        txf = TXFToken()
        txf.create_genesis_block()
        
        tx_type = data.get("type", "OSINT_QUERY")
        if tx_type == "OSINT_QUERY":
            tx = txf.log_osint_query(data.get("query_type", ""), data.get("target", ""), data.get("operator", "user"))
        elif tx_type == "DATA_ACCESS":
            tx = txf.log_data_access(data.get("data_source", ""), data.get("record_count", 0), data.get("accessor", "user"))
        else:
            tx = txf.log_osint_query(data.get("query_type", "unknown"), data.get("target", ""), data.get("operator", "user"))
        
        return jsonify({"success": True, "tx": tx})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/status")
def status_page():
    return render_template_string(HTML, content="<div class='tool-card'><h2>System Status</h2><p>VM: osint-free<br>IP: 136.119.249.79<br>Cost: $0.00</p></div>")

@app.route("/api/email")
def api_email():
    email = request.args.get('email', '')
    return jsonify({"email": email, "status": "scan_complete", "note": "Add OSINT tools here"})

@app.route("/api/domain")
def api_domain():
    domain = request.args.get('domain', '')
    return jsonify({"domain": domain, "status": "scan_complete", "note": "Add OSINT tools here"})

@app.route("/api/gis")
def api_gis():
    dataset = request.args.get('dataset', '')
    data_dir = os.path.expanduser('~/OsintNeoAi/data/huntington_beach')
    try:
        files = {
            'parcels': 'HB_Parcels.json',
            'tracts': 'HB_Tracts.json',
            'zoning': 'HB_Zoning.json',
            'subsidence': 'HB_Subsidence.json',
            'streets': 'HB_Street_Centers.json',
            'cip': 'HB_CIP_Public_Works.json',
            'oil': 'HB_Oil.json',
            'flood': 'HB_FEMA_Flood.json'
        }
        fpath = os.path.join(data_dir, files.get(dataset, ''))
        if os.path.exists(fpath):
            with open(fpath) as f:
                data = json.load(f)
            count = data.get('count', len(data.get('features', [])))
            sample = data.get('features', [])[:3]
            return jsonify({"dataset": dataset, "count": count, "sample": sample})
        return jsonify({"error": "not found"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
