import streamlit as st
import requests
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Network Copilot", layout="wide")

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def load_sidebar_history():
    """Retrieves unique past questions for the sidebar navigation."""
    try:
        conn = sqlite3.connect("data/network_ops.db")
        query = "SELECT id, user_query, ai_response FROM chat_history ORDER BY id DESC LIMIT 10"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

with st.sidebar:
    st.title(" Chat Details")
    
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("Recent Activity")
    
    history_df = load_sidebar_history()
    if not history_df.empty:
        for _, row in history_df.iterrows():
            if st.button(f" {row['user_query'][:25]}...", key=f"chat_{row['id']}", use_container_width=True):
                
                st.session_state.messages = [
                    {"role": "user", "content": row['user_query']},
                    {"role": "assistant", "content": row['ai_response']}
                ]
    
    st.divider()
    st.header("Live Telemetry")

   
    def get_live_data():
        try:
            response = requests.post(f"{API_BASE_URL}/chat", json={"question": "status"}, timeout=5)
            return response.json()
        except:
            return None

    data = get_live_data()
    if data and data.get("status") == "success":
        metrics = data["network_health"]
        status_label = data.get("status_label", "Healthy")
        
        if status_label == "Healthy":
            st.success(f"Status: {status_label}")
        elif status_label == "Degraded":
            st.warning(f"Status: {status_label}")
        else:
            st.error(f"Status: {status_label}")

        if st.button("Refresh"):
            st.rerun()


st.title("Network Copilot Dashboard")

if data and data.get("status") == "success":
    metrics = data["network_health"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Latency", f"{round(metrics.get('latency_ms', 0), 2)} ms")
    m2.metric("Bandwidth", f"{round(metrics.get('bandwidth_mbps', 0), 2)} Mbps")
    m3.metric("Packet Loss", f"{round(metrics.get('packet_loss_rate', 0), 2)} %")
else:
    st.warning("Waiting for Backend connection...")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [] 


for message in st.session_state.messages:
    with st.chat_message(message["role"]):   # Logic to Display only the current active conversation
        st.markdown(message["content"])

if prompt := st.chat_input("How is my network performing?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            res = requests.post(f"{API_BASE_URL}/chat", json={"question": prompt}, timeout=10)
            if res.status_code == 200:
                answer = res.json()["answer"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error("The brain is offline. Check backend.")
        except Exception as e:
            st.error(f"Connection Error: {e}")