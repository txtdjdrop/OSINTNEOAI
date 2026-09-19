# Spec: OsintNeoAi Max-Out — Free Tier VM, Android-First, AI Chat

## Objective

Max out every free-tier capability of the OsintNeoAi forensic intelligence platform on the existing GCP e2-micro VM (`136.119.249.79`), optimized for Android A16 cellphone access, with a full AI chat interface similar to OpenCode — all at $0 cost using only free tiers and trial credits.

**User:** Single operator (Tony) running forensic OSINT investigations from an Android A16 cellphone.

**Success looks like:**
- Full AI chat on phone that can query BigQuery, search evidence, run pipeline phases
- Mobile-optimized dashboard with all controls accessible from touch
- Scheduled scraping running autonomously
- All data backed up to Google Drive
- Zero dollars spent

## Assumptions I'm Making

1. The GCP project `noble-beanbag-497411-m4` remains the BigQuery backend
2. The VM `osint-free` (e2-micro, Debian 12, `blah-905ad` project) is the target
3. "Full AI chat like OpenCode" means a conversational interface that can execute OSINT queries, not a general-purpose LLM
4. "Max out free tier" means use every free service available without triggering billing
5. Android A16 phone is the primary client device (mobile browser)
6. "Trial credit tiers" refers to GCP $300 trial credits — use them only if needed, avoid spending actual money
7. We're building a Flask/web-based chat UI, not installing a native app
8. The user wants to be able to step away and everything keeps running autonomously

## Free Tier Budget (Must Not Exceed)

| Service | Free Tier Limit | Current Usage | Status |
|---------|----------------|---------------|--------|
| GCP Compute (e2-micro) | 1 instance, 30GB disk | Running | ACTIVE |
| BigQuery | 1TB queries/mo, 10GB storage | 10,116 rows | OK |
| Cloud Storage | 5GB | 53MB (GIS) | OK |
| Cloud Run | 2M requests/mo | 0 | AVAILABLE |
| Cloud Build | 120 build-min/day | 0 | AVAILABLE |
| Firestore | 1GB storage | 0 | AVAILABLE |
| Cloud Functions | 2M invocations/mo | 0 | AVAILABLE |
| **DO NOT USE** | Compute Engine (non-e2), GPU, Regional LB | — | BLOCKED |

## Tech Stack

- **VM:** GCP e2-micro, Debian 12, Python 3.11
- **Backend:** Flask (already installed)
- **Database:** BigQuery (existing) + SQLite (local for chat history)
- **Frontend:** Vanilla HTML/CSS/JS (mobile-first, no framework)
- **AI Chat:** Rule-based intent parser + BigQuery executor (no external LLM API — zero cost)
- **Auth:** IP-based or simple token (no OAuth complexity)
- **Scheduling:** Cron (already configured)

## Commands

```
VM SSH:        gcloud compute ssh osint-free --project=blah-905ad --zone=us-central1-a
Dashboard:     http://136.119.249.79:8080
Chat:          http://136.119.249.79:8080/chat
Admin:         http://136.119.249.79:8080/admin
Pipeline API:  http://136.119.249.79:8080/api/pipeline
BigQuery API:  http://136.119.249.79:8080/api/query
Logs:          http://136.119.249.79:8080/api/logs

Start:         sudo systemctl start osintneoai
Stop:          sudo systemctl stop osintneoai
Restart:       sudo systemctl restart osintneoai
Logs:          sudo journalctl -u osintneoai -f
Status:        sudo systemctl status osintneoai
```

## Project Structure

```
/opt/osintneoai/                    # or /home/brainmedus_gmail_com/OsintNeoAi
├── app/
│   ├── __init__.py
│   ├── main.py                     # Flask app entry
│   ├── chat.py                     # AI chat engine (intent parser + executor)
│   ├── queries.py                  # BigQuery query library
│   ├── pipeline.py                 # 7-phase pipeline runner
│   ├── scheduler.py                # Scheduled task manager
│   └── auth.py                     # Simple token auth
├── templates/
│   ├── index.html                  # Mobile dashboard (home)
│   ├── chat.html                   # AI chat interface
│   ├── admin.html                  # System admin panel
│   ├── pipeline.html               # Pipeline control
│   └── base.html                   # Shared mobile layout
├── static/
│   ├── style.css                   # Mobile-first CSS
│   ├── app.js                      # Main JS
│   └── chat.js                     # Chat UI JS
├── data/
│   ├── chat_history.db             # SQLite chat log
│   └── config.json                 # Runtime config
├── tools/
│   ├── edr_historical_scraper.py   # EDR scraper
│   └── ocgis_scraper.py           # OCGIS scraper
├── venv/                           # Python virtual environment
├── requirements.txt
└── osintneoai.service              # Systemd service file
```

## Code Style

```python
# Flask route example
@app.route("/api/query", methods=["POST"])
def api_query():
    """Execute a BigQuery query from chat or dashboard."""
    data = request.get_json()
    sql = data.get("sql", "")
    if not sql:
        return jsonify({"error": "No SQL provided"}), 400
    
    try:
        results = run_bigquery(sql)
        return jsonify({"rows": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

```javascript
// Chat message send
async function sendMessage(text) {
    addMessage(text, "user");
    const resp = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    });
    const data = await resp.json();
    addMessage(data.response, "assistant");
}
```

**Conventions:**
- Python: snake_case functions, UPPER_CASE constants
- JS: camelCase functions
- HTML: semantic tags, data-* attributes for JS hooks
- CSS: BEM-style classes, mobile-first media queries

## Testing Strategy

- **Framework:** pytest (already available)
- **Unit tests:** `tests/` — test chat intent parser, query builder
- **Integration tests:** test BigQuery connectivity, API endpoints
- **Manual verification:** Open `http://136.119.249.79:8080/chat` on phone, type a query, verify response

## Boundaries

- **Always:** Run `python3 -m pytest tests/` before committing, validate SQL before executing, log all chat queries
- **Ask first:** Add new BigQuery tables, change auth model, expose new ports
- **Never:** Commit API keys or ADC files to git, run DELETE/DROP queries, spend actual money

## Success Criteria

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | Chat UI loads on Android A16 browser | Open http://136.119.249.79:8080/chat on phone |
| 2 | Chat can query BigQuery and return results | Type "show EDR hits" → see results |
| 3 | Chat can run pipeline phases | Type "run pipeline" → see execution |
| 4 | Dashboard shows all controls on mobile | Tap all buttons, verify responses |
| 5 | Scheduled scraping works | Cron jobs run at 2AM/3AM |
| 6 | Zero dollars spent | Check GCP billing dashboard |
| 7 | All data backed up to Google Drive | Verify gdrive:Sharedall/OsintNeoAi/ |

## Implementation Plan (Summary)

| Phase | What | Est. Time |
|-------|------|-----------|
| 1 | Mobile dashboard (responsive) | 30 min |
| 2 | AI chat engine (intent parser) | 45 min |
| 3 | Chat UI (mobile-optimized) | 30 min |
| 4 | BigQuery integration | 15 min |
| 5 | Pipeline control via chat | 15 min |
| 6 | Systemd service + auto-start | 10 min |
| 7 | Testing on Android A16 | 15 min |

**Total: ~2.5 hours**
