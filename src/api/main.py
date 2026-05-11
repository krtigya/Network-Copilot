import sqlite3
import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# LangChain for RAG
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

app = FastAPI(title="Network Copilot API")

class ChatRequest(BaseModel):
    question: str


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

if os.path.exists("faiss_index"):
    vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    print("FAISS Vector Index Loaded Successfully.")
else:
    vector_db = None
    print("Warning: 'faiss_index' folder not found. RAG features disabled.")


DB_PATH = os.path.join("data", "network_ops.db")

def init_db():
    """Ensure the necessary tables exist before the API starts."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_chat(user_query: str, ai_response: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_query, ai_response) VALUES (?, ?)", 
            (user_query, ai_response)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f" DB SAVE ERROR: {e}")

def get_network_diagnostics():
    """Fetches the single latest telemetry row from SQL."""
    try:
        if not os.path.exists(DB_PATH):
            return {"error": "DB missing"}
            
        conn = sqlite3.connect(DB_PATH)
        # Fetch the most recent log
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM network_logs ORDER BY ROWID DESC LIMIT 1')
        row = cursor.fetchone()
        
        # Dynamically get column names
        cursor.execute("PRAGMA table_info(network_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        if row:
            return dict(zip(columns, row))
        return {"message": "No data available"}
    except Exception as e:
        return {"error": str(e)}

def search_manuals(query: str):
    """Retrieves context from FAISS and cleans the formatting."""
    if not vector_db:
        return "Technical documentation is currently unavailable."
    try:
        docs = vector_db.similarity_search(query, k=2)
        content = " ".join([doc.page_content for doc in docs])
        return content.strip()
    except Exception as e:
        return f"Error retrieving manuals: {e}"


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    diagnostics = get_network_diagnostics()
    
    lat = diagnostics.get('latency_ms', 0) or 0
    loss = diagnostics.get('packet_loss_rate', 0) or 0
    bw = diagnostics.get('bandwidth_mbps', 0) or 0
    
    user_q = request.question.lower()
    
    if "status" in user_q or "how is my network" in user_q:
        advice_content = "Please refer to the dashboard metrics above for live performance visualization."
    elif "ip" in user_q or "address" in user_q:
        ip = diagnostics.get('device_ip', '127.0.0.1')
        advice_content = f"The management IP for the reported node is: **{ip}**."
    else:
        
        raw_advice = search_manuals(request.question)
        # Format as a nice bulleted list
        advice_content = raw_advice.replace(". ", ".\n\n* ")
        if not advice_content.startswith("* "):
            advice_content = "* " + advice_content
    
    
    if loss > 1.0:
        status_label = "Degraded"
        reasoning = f"Alert: **{round(loss, 2)}% packet loss** detected."
    elif lat > 100:
        status_label = "Lagging"
        reasoning = f"High latency detected: **{round(lat, 2)}ms**."
    elif bw < 20 and bw > 0:
        status_label = "Slow"
        reasoning = "Bandwidth is significantly below the 20Mbps threshold."
    else:
        status_label = "Healthy"
        reasoning = "All telemetry metrics are within nominal operating range."

    
    final_answer = f"**Status:** {status_label}\n\n{reasoning}\n\n### Troubleshooting Advice\n{advice_content}"

 
    if "status" not in user_q: 
        save_chat(request.question, final_answer)

    return {
        "status": "success",
        "status_label": status_label,
        "network_health": diagnostics,
        "answer": final_answer
    }


if __name__ == "__main__":
    init_db() 
    print("\n" + " NETWORK COPILOT API STARTING".center(40, "="))
    # Using 127.0.0.1 for local, 0.0.0.0 for Docker
    uvicorn.run(app, host="127.0.0.1", port=8000)