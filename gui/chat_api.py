"""FastAPI backend for Gemini Data Analytics Chat"""
import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="OSINT Neo AI Chat API")

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BigQuery client
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "blah-905ad")
DATASET_ID = "osint_investigation"

# Table references for Gemini DataChat
TABLE_REFERENCES = [
    {"project_id": PROJECT_ID, "dataset_id": DATASET_ID, "table_id": "breach_results"},
    {"project_id": PROJECT_ID, "dataset_id": DATASET_ID, "table_id": "grants_tracked"},
    {"project_id": PROJECT_ID, "dataset_id": DATASET_ID, "table_id": "hbnc_entities"},
]


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


class ChatResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    results: Optional[list] = None


@app.get("/health")
async def health():
    return {"status": "ok", "project": PROJECT_ID, "dataset": DATASET_ID}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat queries using BigQuery SQL generation"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        # Simple intent detection for SQL generation
        sql_query = generate_sql(request.message)
        
        if sql_query:
            # Execute query
            result = client.query(sql_query).to_dataframe()
            results = result.to_dict(orient="records")
            
            # Generate response
            response = format_response(request.message, results, sql_query)
            
            return ChatResponse(
                response=response,
                sql_query=sql_query,
                results=results
            )
        else:
            return ChatResponse(
                response="I can help you query the OSINT investigation data. Try asking about:\n- Breach analysis (e.g., 'Show compromised emails')\n- Grant tracking (e.g., 'List all flagged grants')\n- HBNC entities (e.g., 'Show all contractors')\n- Risk assessment (e.g., 'What are the critical risks?')",
                sql_query=None,
                results=None
            )
    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            sql_query=None,
            results=None
        )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming version of chat endpoint"""
    async def generate():
        try:
            client = bigquery.Client(project=PROJECT_ID)
            sql_query = generate_sql(request.message)
            
            if sql_query:
                yield f"data: {json.dumps({'type': 'THOUGHT', 'content': f'Generating SQL query: {sql_query}'})}\n\n"
                
                result = client.query(sql_query).to_dataframe()
                results = result.to_dict(orient="records")
                
                yield f"data: {json.dumps({'type': 'THOUGHT', 'content': f'Found {len(results)} results'})}\n\n"
                
                response = format_response(request.message, results, sql_query)
                yield f"data: {json.dumps({'type': 'FINAL_RESPONSE', 'content': response})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'FINAL_RESPONSE', 'content': 'I can help you query the OSINT data. Ask about breaches, grants, or entities.'})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'FINAL_RESPONSE', 'content': f'Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


def generate_sql(message: str) -> Optional[str]:
    """Generate SQL based on user intent"""
    message_lower = message.lower()
    
    # Breach queries
    if any(word in message_lower for word in ["breach", "compromised", "hack", "leak", "security"]):
        if any(word in message_lower for word in ["critical", "high risk", "most"]):
            return f"SELECT email, breaches, sources, risk_level FROM `{PROJECT_ID}.{DATASET_ID}.breach_results` WHERE risk_level IN ('CRITICAL', 'HIGH') ORDER BY breaches DESC"
        elif any(word in message_lower for word in ["count", "how many", "total"]):
            return f"SELECT COUNT(*) as total_breached, COUNTIF(risk_level='CRITICAL') as critical, COUNTIF(risk_level='HIGH') as high FROM `{PROJECT_ID}.{DATASET_ID}.breach_results` WHERE status='COMPROMISED'"
        else:
            return f"SELECT email, status, breaches, sources, risk_level FROM `{PROJECT_ID}.{DATASET_ID}.breach_results` WHERE status='COMPROMISED' ORDER BY breaches DESC"
    
    # Grant queries
    elif any(word in message_lower for word in ["grant", "funding", "money", "award", "spending"]):
        if any(word in message_lower for word in ["flagged", "suspicious", "audit"]):
            return f"SELECT recipient_name, amount_usd, funding_agency, status FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked` WHERE status LIKE '%FLAGGED%' ORDER BY amount_usd DESC"
        elif any(word in message_lower for word in ["total", "sum", "how much"]):
            return f"SELECT SUM(amount_usd) as total_funding, COUNT(*) as total_grants FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked`"
        elif any(word in message_lower for word in ["top", "largest", "biggest"]):
            return f"SELECT recipient_name, amount_usd, purpose FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked` ORDER BY amount_usd DESC LIMIT 5"
        else:
            return f"SELECT recipient_name, amount_usd, funding_agency, status, purpose FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked` ORDER BY amount_usd DESC"
    
    # Entity queries
    elif any(word in message_lower for word in ["entity", "contractor", "company", "who", "organization"]):
        if any(word in message_lower for word in ["contractor", "vendor"]):
            return f"SELECT entity_name, role, organization, notes FROM `{PROJECT_ID}.{DATASET_ID}.hbnc_entities` WHERE entity_type='Contractor'"
        elif any(word in message_lower for word in ["government", "city", "official"]):
            return f"SELECT entity_name, role, organization, notes FROM `{PROJECT_ID}.{DATASET_ID}.hbnc_entities` WHERE entity_type='Government'"
        else:
            return f"SELECT entity_name, entity_type, role, organization, notes FROM `{PROJECT_ID}.{DATASET_ID}.hbnc_entities`"
    
    # Risk assessment
    elif any(word in message_lower for word in ["risk", "threat", "danger", "warning"]):
        return f"""
        SELECT 'Breach Risk' as category, email as item, risk_level as risk, breaches as score 
        FROM `{PROJECT_ID}.{DATASET_ID}.breach_results` 
        WHERE risk_level IN ('CRITICAL', 'HIGH')
        UNION ALL
        SELECT 'Grant Risk' as category, recipient_name as item, 'FLAGGED' as risk, amount_usd/1000000 as score
        FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked` 
        WHERE status LIKE '%FLAGGED%'
        ORDER BY score DESC
        """
    
    # HBNC specific
    elif any(word in message_lower for word in ["hbnc", "navigation center", "shelter", "homeless"]):
        return f"SELECT entity_name, role, organization, notes FROM `{PROJECT_ID}.{DATASET_ID}.hbnc_entities` WHERE notes LIKE '%shelter%' OR notes LIKE '%HBNC%' OR notes LIKE '%Beach%'"
    
    # Summary
    elif any(word in message_lower for word in ["summary", "overview", "status", "report"]):
        return f"""
        SELECT 'Breaches' as metric, COUNTIF(status='COMPROMISED') as value FROM `{PROJECT_ID}.{DATASET_ID}.breach_results`
        UNION ALL
        SELECT 'Total Grants', SUM(amount_usd)/1000000 FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked`
        UNION ALL
        SELECT 'Flagged Grants', COUNT(*) FROM `{PROJECT_ID}.{DATASET_ID}.grants_tracked` WHERE status LIKE '%FLAGGED%'
        UNION ALL
        SELECT 'Entities', COUNT(*) FROM `{PROJECT_ID}.{DATASET_ID}.hbnc_entities`
        """
    
    return None


def format_response(message: str, results: list, sql_query: str) -> str:
    """Format query results into readable response"""
    if not results:
        return "No results found for your query."
    
    # Summary response
    if len(results) == 1 and len(results[0]) <= 4:
        values = list(results[0].values())
        keys = list(results[0].keys())
        response = "**Summary:**\n"
        for k, v in zip(keys, values):
            if isinstance(v, float):
                response += f"- {k}: ${v:,.2f}\n" if "amount" in k.lower() else f"- {k}: {v:,.2f}\n"
            else:
                response += f"- {k}: {v}\n"
        return response
    
    # Table response
    response = f"**Results ({len(results)} rows):**\n\n"
    headers = list(results[0].keys())
    
    # Markdown table
    response += "| " + " | ".join(headers) + " |\n"
    response += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    for row in results[:20]:  # Limit to 20 rows
        values = []
        for h in headers:
            v = row.get(h, "")
            if isinstance(v, float):
                values.append(f"${v:,.2f}" if "amount" in h.lower() else f"{v:,.2f}")
            else:
                values.append(str(v)[:50])
        response += "| " + " | ".join(values) + " |\n"
    
    if len(results) > 20:
        response += f"\n... and {len(results) - 20} more rows"
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
