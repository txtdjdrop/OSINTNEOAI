#!/usr/bin/env python3
"""Integrate TaxFunded grant data into OSINT newspaper and TXF ledger"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / "OsintNeoAi" / "data"
GRANTS_DIR = DATA_DIR / "grants"
NEWSPAPER_DIR = DATA_DIR / "ledger"
LEDGER_DIR = DATA_DIR / "ledger"

# Grant data from TaxFunded
GRANTS_DATA = [
    {
        "id": "fed-coc-2025-01",
        "title": "HUD Continuum of Care (CoC) Program Competition",
        "agency": "U.S. Department of Housing and Urban Development (HUD)",
        "jurisdiction": "Federal",
        "category": "Homelessness & CoC",
        "fundingType": "Discretionary Grant",
        "amountRange": "$100,000 - $5,000,000",
        "deadline": "2026-10-15",
        "description": "Annual federal funding to support community-based homelessness housing and service interventions.",
        "recipients": [
            {"name": "LAHSA", "amount": "$142,500,000", "year": 2025, "location": "Los Angeles, CA"},
            {"name": "PATH", "amount": "$8,400,000", "year": 2024, "location": "San Diego, CA"},
            {"name": "Abode Services", "amount": "$12,100,000", "year": 2025, "location": "Alameda County, CA"},
        ],
        "sourceUrl": "https://www.hud.gov/program_offices/comm_planning/coc"
    },
    {
        "id": "ca-hcd-mhsa-2025",
        "title": "California MHSA Community Services Investment",
        "agency": "California Department of Housing and Community Development (HCD)",
        "jurisdiction": "California",
        "category": "Homelessness & CoC",
        "fundingType": "Formula Grant",
        "amountRange": "$50,000 - $2,000,000",
        "deadline": "2026-11-01",
        "description": "State funding for mental health services and housing support.",
        "recipients": [],
        "sourceUrl": "https://www.hcd.ca.gov"
    },
    {
        "id": "fed-coc-hbnc-2025",
        "title": "Huntington Beach Navigation Center Funding",
        "agency": "HUD / City of Huntington Beach",
        "jurisdiction": "Both",
        "category": "Homelessness & CoC",
        "fundingType": "Discretionary Grant",
        "amountRange": "$2,000,000 - $5,000,000",
        "deadline": "2025-12-31",
        "description": "Local funding for HBNC operations and shelter expansion.",
        "recipients": [
            {"name": "Mercy House", "amount": "$2,596,240", "year": 2025, "location": "Huntington Beach, CA"},
            {"name": "Jamboree Housing", "amount": "$3,214,035", "year": 2025, "location": "Huntington Beach, CA"},
        ],
        "sourceUrl": "https://www.huntingtonbeachca.gov"
    },
]


def ensure_dirs():
    """Ensure directories exist"""
    os.makedirs(GRANTS_DIR, exist_ok=True)
    os.makedirs(NEWSPAPER_DIR, exist_ok=True)
    os.makedirs(LEDGER_DIR, exist_ok=True)


def save_grants_data():
    """Save grants data to JSON"""
    ensure_dirs()
    
    with open(GRANTS_DIR / "grants_data.json", "w") as f:
        json.dump(GRANTS_DATA, f, indent=2)
    
    print(f"Saved {len(GRANTS_DATA)} grants to {GRANTS_DIR / 'grants_data.json'}")


def add_grants_to_newspaper():
    """Add grant articles to the OSINT newspaper"""
    ensure_dirs()
    
    articles = []
    for grant in GRANTS_DATA:
        article = {
            "id": hashlib.md5(grant["id"].encode()).hexdigest()[:12],
            "source": "taxfunded_grants",
            "file": f"{grant['id']}.json",
            "title": grant["title"],
            "summary": grant["description"],
            "timestamp": datetime.now().isoformat(),
            "size": len(json.dumps(grant)),
            "hyperlinks": [grant["sourceUrl"]],
            "tags": [
                grant["category"],
                grant["jurisdiction"],
                grant["fundingType"],
                "Grant",
                "Taxpayer Funded",
            ],
            "grant_data": grant,
        }
        articles.append(article)
    
    # Load existing newspaper data
    newspaper_path = NEWSPAPER_DIR / "newspaper.json"
    if newspaper_path.exists():
        with open(newspaper_path) as f:
            newspaper = json.load(f)
    else:
        newspaper = {
            "generated_at": datetime.now().isoformat(),
            "total_articles": 0,
            "sources": [],
            "articles": [],
            "stats": {"total_hyperlinks": 0, "total_tags": 0, "sources_breakdown": {}},
        }
    
    # Add new articles
    existing_ids = {a["id"] for a in newspaper["articles"]}
    for article in articles:
        if article["id"] not in existing_ids:
            newspaper["articles"].append(article)
    
    # Update stats
    newspaper["total_articles"] = len(newspaper["articles"])
    newspaper["sources"] = list(set(a["source"] for a in newspaper["articles"]))
    newspaper["stats"]["total_hyperlinks"] = sum(len(a["hyperlinks"]) for a in newspaper["articles"])
    newspaper["stats"]["total_tags"] = len(set(t for a in newspaper["articles"] for t in a["tags"]))
    
    for a in newspaper["articles"]:
        src = a["source"]
        newspaper["stats"]["sources_breakdown"][src] = newspaper["stats"]["sources_breakdown"].get(src, 0) + 1
    
    with open(newspaper_path, "w") as f:
        json.dump(newspaper, f, indent=2)
    
    print(f"Added {len(articles)} grant articles to newspaper")


def add_grants_to_ledger():
    """Add grant transactions to TXF ledger"""
    ensure_dirs()
    
    ledger_path = LEDGER_DIR / "txf_ledger.json"
    if ledger_path.exists():
        with open(ledger_path) as f:
            ledger = json.load(f)
    else:
        ledger = {
            "token": {"name": "TXF", "symbol": "TXF", "total_supply": 0},
            "blocks": [],
            "transactions": [],
            "balances": {},
            "stats": {"total_blocks": 0, "total_transactions": 0, "total_supply": 0, "balances": {}},
        }
    
    # Add grant transactions
    for grant in GRANTS_DATA:
        for recipient in grant.get("recipients", []):
            amount_str = recipient["amount"].replace("$", "").replace(",", "")
            try:
                amount = int(amount_str)
            except ValueError:
                amount = 0
            
            tx = {
                "type": "GRANT_AWARD",
                "grant_id": grant["id"],
                "grant_title": grant["title"],
                "recipient": recipient["name"],
                "amount": amount,
                "location": recipient.get("location", ""),
                "year": recipient.get("year", 2025),
                "agency": grant["agency"],
                "jurisdiction": grant["jurisdiction"],
                "timestamp": datetime.now().isoformat(),
                "tx_hash": hashlib.sha256(f"{grant['id']}:{recipient['name']}:{amount}".encode()).hexdigest()[:16],
            }
            
            ledger["transactions"].append(tx)
            
            # Update balances
            ledger["balances"][recipient["name"]] = ledger["balances"].get(recipient["name"], 0) + amount
            ledger["balances"]["GRANT_POOL"] = ledger["balances"].get("GRANT_POOL", 0) + amount
            ledger["token"]["total_supply"] += amount
    
    # Update stats
    ledger["stats"]["total_blocks"] = len(ledger["blocks"]) + 1
    ledger["stats"]["total_transactions"] = len(ledger["transactions"])
    ledger["stats"]["total_supply"] = ledger["token"]["total_supply"]
    ledger["stats"]["balances"] = ledger["balances"]
    
    with open(ledger_path, "w") as f:
        json.dump(ledger, f, indent=2)
    
    print(f"Added {sum(len(g.get('recipients', [])) for g in GRANTS_DATA)} grant transactions to ledger")


def generate_newspaper_html():
    """Generate updated newspaper HTML"""
    newspaper_path = NEWSPAPER_DIR / "newspaper.json"
    if not newspaper_path.exists():
        print("No newspaper data found")
        return
    
    with open(newspaper_path) as f:
        newspaper = json.load(f)
    
    html = '<!DOCTYPE html>\n<html>\n<head>\n'
    html += '<title>OSINT Neo AI - Intelligence Newspaper</title>\n'
    html += '<style>\n'
    html += '* { margin:0; padding:0; box-sizing:border-box; }\n'
    html += "body { font-family:'Georgia',serif; background:#fafaf8; color:#1a1a1a; }\n"
    html += '.masthead { background:#1a1a1a; color:#fff; text-align:center; padding:30px; }\n'
    html += '.masthead h1 { font-size:48px; letter-spacing:4px; }\n'
    html += '.masthead .dateline { color:#888; margin-top:10px; font-style:italic; }\n'
    html += '.stats-bar { background:#f0f0f0; padding:10px 30px; display:flex; gap:30px; border-bottom:2px solid #1a1a1a; }\n'
    html += '.stats-bar .stat { font-size:12px; color:#666; }\n'
    html += '.stats-bar .stat b { color:#1a1a1a; }\n'
    html += '.container { max-width:1200px; margin:0 auto; padding:20px; }\n'
    html += '.article { background:#fff; border:1px solid #ddd; padding:20px; margin:15px 0; }\n'
    html += '.article h2 { font-size:24px; margin-bottom:10px; }\n'
    html += '.article .meta { color:#888; font-size:12px; margin-bottom:10px; }\n'
    html += '.article .summary { line-height:1.6; margin-bottom:10px; }\n'
    html += '.article .tags { display:flex; flex-wrap:wrap; gap:5px; }\n'
    html += '.article .tag { background:#e8e8e8; padding:2px 8px; font-size:11px; border-radius:3px; }\n'
    html += '.grant-badge { background:#00ff41; color:#000; padding:2px 8px; font-size:11px; font-weight:bold; border-radius:3px; }\n'
    html += '</style>\n</head>\n<body>\n'
    
    html += '<div class="masthead">\n'
    html += '<h1>OSINT NEO AI</h1>\n'
    html += '<div class="dateline">Intelligence Newspaper | Generated: ' + newspaper["generated_at"][:10] + '</div>\n'
    html += '</div>\n'
    
    html += '<div class="stats-bar">\n'
    html += '<div class="stat"><b>' + str(newspaper["total_articles"]) + '</b> Articles</div>\n'
    html += '<div class="stat"><b>' + str(newspaper["stats"]["total_hyperlinks"]) + '</b> Hyperlinks</div>\n'
    html += '<div class="stat"><b>' + str(newspaper["stats"]["total_tags"]) + '</b> Tags</div>\n'
    html += '<div class="stat"><b>' + str(len(newspaper["sources"])) + '</b> Sources</div>\n'
    html += '</div>\n'
    
    html += '<div class="container">\n'
    for article in newspaper["articles"]:
        html += '<div class="article">\n'
        html += '<h2>' + article["title"] + '</h2>\n'
        html += '<div class="meta">Source: ' + article["source"] + ' | ' + article["timestamp"][:10] + '</div>\n'
        html += '<div class="summary">' + article["summary"] + '</div>\n'
        
        if article.get("grant_data", {}).get("recipients"):
            html += '<div style="margin:10px 0; padding:10px; background:#f0f8f0; border-left:3px solid #00ff41;">\n'
            html += '<b>Recipients:</b><br>\n'
            for r in article["grant_data"]["recipients"]:
                html += '<span class="grant-badge">' + r["amount"] + '</span> ' + r["name"] + ' (' + r.get("location", "") + ')<br>\n'
            html += '</div>\n'
        
        html += '<div class="tags">\n'
        for t in article["tags"]:
            html += '<span class="tag">' + t + '</span>\n'
        html += '</div>\n'
        
        if article["hyperlinks"]:
            html += '<div style="margin-top:10px;">\n'
            for url in article["hyperlinks"][:3]:
                html += '<a href="' + url + '" target="_blank" style="color:#0066cc; font-size:12px; margin-right:10px;">Source</a>\n'
            html += '</div>\n'
        
        html += '</div>\n'
    html += '</div>\n'
    html += '</body>\n</html>'
    
    with open(NEWSPAPER_DIR / "newspaper.html", "w") as f:
        f.write(html)
    
    print("Generated updated newspaper HTML")


def generate_ledger_html():
    """Generate updated TXF ledger HTML"""
    ledger_path = LEDGER_DIR / "txf_ledger.json"
    if not ledger_path.exists():
        print("No ledger data found")
        return
    
    with open(ledger_path) as f:
        ledger = json.load(f)
    
    stats = ledger["stats"]
    
    html = '<!DOCTYPE html>\n<html>\n<head>\n'
    html += '<title>TXF Token - Taxpayer OSINT Ledger</title>\n'
    html += '<style>\n'
    html += '* { margin:0; padding:0; box-sizing:border-box; }\n'
    html += "body { font-family:'Courier New',monospace; background:#0a0a0a; color:#00ff41; }\n"
    html += '.header { background:#111; padding:30px; border-bottom:2px solid #00ff41; }\n'
    html += '.header h1 { font-size:36px; }\n'
    html += '.container { max-width:1200px; margin:0 auto; padding:20px; }\n'
    html += ".stats { display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin:20px 0; }\n"
    html += '.stat-box { background:#111; border:1px solid #333; padding:15px; text-align:center; }\n'
    html += '.stat-box .number { font-size:28px; font-weight:bold; color:#00ff41; }\n'
    html += '.stat-box .label { font-size:11px; color:#888; margin-top:5px; }\n'
    html += '.balances { background:#111; border:1px solid #333; padding:20px; margin-top:20px; }\n'
    html += '.balances h2 { color:#00ff41; margin-bottom:15px; }\n'
    html += '.balance-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #222; }\n'
    html += '.balance-address { color:#888; }\n'
    html += '.balance-amount { color:#00ff41; font-weight:bold; }\n'
    html += '.ledger { background:#111; border:1px solid #333; padding:20px; margin-top:20px; }\n'
    html += '.ledger h2 { color:#00ff41; margin-bottom:15px; }\n'
    html += '.tx { border-bottom:1px solid #222; padding:8px 0; font-size:12px; }\n'
    html += '.tx-type { color:#00ff41; font-weight:bold; }\n'
    html += '</style>\n</head>\n<body>\n'
    
    html += '<div class="header">\n'
    html += '<h1>&#127981; TXF TOKEN</h1>\n'
    html += '<p>Taxpayer OSINT Ledger | TXF | Block #' + str(stats["total_blocks"]) + '</p>\n'
    html += '</div>\n'
    
    html += '<div class="container">\n'
    html += '<div class="stats">\n'
    html += '<div class="stat-box"><div class="number">' + str(stats["total_blocks"]) + '</div><div class="label">Blocks</div></div>\n'
    html += '<div class="stat-box"><div class="number">' + str(stats["total_transactions"]) + '</div><div class="label">Transactions</div></div>\n'
    html += '<div class="stat-box"><div class="number">' + str(stats["total_supply"]) + '</div><div class="label">Total Supply</div></div>\n'
    html += '<div class="stat-box"><div class="number">' + str(len(stats["balances"])) + '</div><div class="label">Accounts</div></div>\n'
    html += '</div>\n'
    
    html += '<div class="balances">\n<h2>Account Balances</h2>\n'
    for addr, bal in sorted(stats["balances"].items(), key=lambda x: -x[1])[:20]:
        html += '<div class="balance-item"><div class="balance-address">' + addr + '</div><div class="balance-amount">' + str(bal) + ' TXF</div></div>\n'
    html += '</div>\n'
    
    html += '<div class="ledger">\n<h2>Grant Transactions</h2>\n'
    for tx in ledger["transactions"][-20:]:
        html += '<div class="tx"><span class="tx-type">[' + tx["type"] + ']</span> '
        html += tx.get("recipient", "") + ' - $' + str(tx.get("amount", 0))
        html += ' (' + tx.get("grant_title", "")[:50] + ')</div>\n'
    html += '</div>\n'
    
    html += '</div>\n</body>\n</html>'
    
    with open(LEDGER_DIR / "txf_ledger.html", "w") as f:
        f.write(html)
    
    print("Generated updated ledger HTML")


if __name__ == "__main__":
    print("Integrating TaxFunded grant data into OSINT Neo AI...\n")
    save_grants_data()
    add_grants_to_newspaper()
    add_grants_to_ledger()
    generate_newspaper_html()
    generate_ledger_html()
    print("\nDone! Grant data integrated.")
