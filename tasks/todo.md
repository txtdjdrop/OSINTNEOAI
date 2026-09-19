# Tasks: OsintNeoAi Max-Out

## Phase 1: Mobile Dashboard
- [ ] Task 1: Build responsive mobile-first base template
  - Acceptance: `base.html` with viewport meta, touch-friendly nav, mobile grid
  - Verify: Opens on Android browser, no horizontal scroll
  - Files: `templates/base.html`, `static/style.css`

- [ ] Task 2: Build dashboard home page
  - Acceptance: 4-card grid (BigQuery, Pipeline, System, Intel), buttons work
  - Verify: Tap each card, see live data from VM
  - Files: `templates/index.html`, `app/main.py`

## Phase 2: AI Chat Engine
- [ ] Task 3: Create SQLite chat history database
  - Acceptance: `chat_history.db` with messages table, auto-create on first run
  - Verify: DB exists after first chat message
  - Files: `app/chat.py`, `data/chat_history.db`

- [ ] Task 4: Build intent parser (zero-cost, no LLM)
  - Acceptance: Parses natural language into structured commands (show/scan/run/search)
  - Verify: "show EDR hits" → `{action: "query", target: "edr_hits"}`, "run pipeline" → `{action: "pipeline"}`
  - Files: `app/chat.py`

- [ ] Task 5: Wire intent parser to BigQuery executor
  - Acceptance: Chat query returns actual BigQuery results as formatted text
  - Verify: Type "show me all parcels" → see APN data in chat
  - Files: `app/chat.py`, `app/queries.py`

## Phase 3: Chat UI
- [ ] Task 6: Build chat HTML template (mobile-first)
  - Acceptance: Message bubbles, input bar fixed to bottom, auto-scroll, typing indicator
  - Verify: Open on phone, send message, see response
  - Files: `templates/chat.html`, `static/chat.js`

- [ ] Task 7: Add chat API endpoint
  - Acceptance: POST /api/chat accepts message, returns response, saves to history
  - Verify: curl test works, chat UI receives response
  - Files: `app/main.py`, `app/chat.py`

## Phase 4: BigQuery Integration
- [ ] Task 8: Create query library (pre-built queries)
  - Acceptance: 10+ named queries (edr_summary, parcels, top_files, timeline, etc.)
  - Verify: Each query returns valid results from BigQuery
  - Files: `app/queries.py`

- [ ] Task 9: Add query shortcuts to chat
  - Acceptance: "edr summary" / "show parcels" / "top files" trigger pre-built queries
  - Verify: Type shortcut, get formatted results
  - Files: `app/chat.py`, `app/queries.py`

## Phase 5: Pipeline Control
- [ ] Task 10: Build pipeline runner API
  - Acceptance: POST /api/pipeline/run triggers 7-phase pipeline, returns progress
  - Verify: API call starts pipeline, status endpoint shows progress
  - Files: `app/pipeline.py`, `app/main.py`

- [ ] Task 11: Wire pipeline to chat
  - Acceptance: "run pipeline" or "run EDR scan" triggers execution via chat
  - Verify: Type command in chat, see pipeline output
  - Files: `app/chat.py`, `app/pipeline.py`

## Phase 6: Service & Deployment
- [ ] Task 12: Create systemd service
  - Acceptance: `osintneoai.service` runs Flask app on boot, auto-restart
  - Verify: `sudo systemctl status osintneoai` shows active
  - Files: `osintneoai.service`, deploy script

- [ ] Task 13: Deploy to VM
  - Acceptance: All files uploaded, service running, dashboard accessible
  - Verify: Open http://136.119.249.79:8080 on phone
  - Files: All (via SCP)

## Phase 7: Verify on Android
- [ ] Task 14: Test full flow on Android A16
  - Acceptance: Dashboard loads, chat works, queries return data, pipeline runs
  - Verify: Use phone for 10 minutes, everything responsive
  - Files: None (manual test)

- [ ] Task 15: Verify zero cost
  - Acceptance: GCP billing shows $0.00 actual spend
  - Verify: Check billing dashboard
  - Files: None (manual check)

## Task Dependencies

```
Task 1 → Task 2 (dashboard needs base template)
Task 3 → Task 4 → Task 5 (chat needs DB, parser, executor)
Task 6 → Task 7 (UI needs API)
Task 8 → Task 9 (shortcuts need queries)
Task 10 → Task 11 (chat needs pipeline API)
Task 12 → Task 13 (deploy needs service)
Task 14 → Task 15 (verify before billing check)
```

## Parallelizable Tasks

- Tasks 1-2 (dashboard) can run in parallel with Tasks 3-5 (chat engine)
- Task 8 (queries) can run in parallel with Tasks 6-7 (chat UI)
- Tasks 10-11 (pipeline) depend on Task 4 (intent parser)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| BigQuery quota exceeded | Chat stops working | Cache query results locally, rate limit queries |
| VM runs out of disk | Service crashes | Monitor disk usage, alert at 80% |
| Port 8080 blocked on phone network | Can't access | Use Cloudflare Tunnel as backup |
| Chat intent parser too rigid | Bad UX | Add fallback "I don't understand" + suggest commands |
