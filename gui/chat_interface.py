"""
OSINT Neo AI - Chat Interface Component
Gemini-powered natural language query interface for BigQuery data
"""

import streamlit as st
import requests
import json
from typing import List, Dict

CHAT_API_URL = "http://localhost:8083"

def init_chat_state():
    """Initialize chat session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_chat_panel(IS_DARK: bool):
    """Render the chat interface"""
    init_chat_state()
    
    bg = "#09090b" if IS_DARK else "#ffffff"
    card = "#0c0c0f" if IS_DARK else "#ffffff"
    border = "#1e1e24" if IS_DARK else "#e4e4e7"
    text = "#fafafa" if IS_DARK else "#09090b"
    text_muted = "#71717a"
    accent = "#2563eb"
    
    st.markdown(f"""
    <style>
    .chat-container {{
        background: {card};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    .chat-message {{
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        line-height: 1.5;
    }}
    .chat-user {{
        background: {accent};
        color: white;
        margin-left: 20%;
    }}
    .chat-assistant {{
        background: {border};
        color: {text};
        margin-right: 20%;
    }}
    .chat-input {{
        width: 100%;
        padding: 0.75rem;
        border: 1px solid {border};
        border-radius: 8px;
        background: {card};
        color: {text};
        font-size: 0.85rem;
    }}
    .suggestion-chip {{
        display: inline-block;
        padding: 4px 12px;
        margin: 4px;
        border-radius: 16px;
        border: 1px solid {border};
        background: {card};
        color: {text_muted};
        font-size: 0.75rem;
        cursor: pointer;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Chat header
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
        <div style="width: 32px; height: 32px; background: {accent}; border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; color: white; 
                    font-weight: 700; font-size: 0.8rem;">AI</div>
        <div>
            <div style="font-weight: 600; color: {text}; font-size: 0.9rem;">OSINT Chat Assistant</div>
            <div style="font-size: 0.72rem; color: {text_muted};">Powered by Gemini Data Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion chips
    suggestions = [
        "Show compromised emails",
        "List flagged grants",
        "Show all contractors",
        "What are the critical risks?",
        "Grant funding summary",
        "HBNC entity overview"
    ]
    
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message chat-user">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message chat-assistant">
                <strong>Assistant:</strong><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input(
        "Ask about the investigation data...",
        key="chat_input",
        placeholder="e.g., Show me all compromised emails with their breach sources"
    )
    
    if st.button("Send", key="send_button") and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Call API
        try:
            response = requests.post(
                f"{CHAT_API_URL}/api/chat",
                json={
                    "message": user_input,
                    "history": st.session_state.chat_history
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_response = data.get("response", "No response")
                sql_query = data.get("sql_query")
                
                # Add SQL query if available
                if sql_query:
                    assistant_response += f"\n\n`SQL: {sql_query}`"
                
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "model", "content": assistant_response})
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"API Error: {response.status_code}"
                })
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Chat API not available. Make sure the chat server is running on port 8083."
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}"
            })
        
        st.rerun()
    
    # Clear chat button
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
