import sqlite3
import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# This Imports for RAG
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Here I Initialize FastAPI app
app = FastAPI(title="Network Copilot API")

# This class helps to Define Request/Response Models
class ChatRequest(BaseModel):
    question: str

# I Loaded the Knowledge Base (RAG)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
if os.path.exists("faiss_index"):
    # this allow_dangerous_deserialization is required for loading local pkl files safely
    vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    vector_db = None
    print(" Warning: faiss_index folder not found. RAG features will be unavailable.")

def search_manuals(query: str):
    """This helps to Retrieves technical advice from FAISS vector index."""
    if not vector_db:
        return "Network manuals are currently offline. Please check physical hardware."
    try:
        # This Retrieve the top 2 most relevant document chunks
        docs = vector_db.similarity_search(query, k=2)
        return " ".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"FAISS Search Error: {e}")
        return "Troubleshooting step: Please restart your router and modem."

# This is the Diagnostic Tool (SQL Telemetry)
def get_network_diagnostics(device_ip: str = "192.168.1.1"):
    try:
        db_path = "data/network_ops.db"
        if not os.path.exists(db_path):
            return {"error": "Database file not found."}
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # This is Use ROW-ID to get the latest telemetry entry from your dataset
        cursor.execute('SELECT * FROM network_logs ORDER BY ROWID DESC LIMIT 1')
        row = cursor.fetchone()
        
        cursor.execute("PRAGMA table_info(network_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        if row:
            return dict(zip(columns, row))
            
        return {"message": "Table is empty."}
    except Exception as e:
        print(f" DATABASE CRASH: {e}")
        return {"error": str(e)}

# This is The API Endpoint (Final Agentic Logic)
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Here I Fetch live telemetry from SQL
    diagnostics = get_network_diagnostics()
    
    # This is the Extract specific metrics for the reasoning engine
    lat = diagnostics.get('latency_ms', 0)
    loss = diagnostics.get('packet_loss_rate', 0)
    bw = diagnostics.get('bandwidth_mbps', 0)
    
    # IT Search the Knowledge Base for advice
    raw_advice = search_manuals(request.question)
    
    # THis is were the FORMATTING FIX: Convert long block of advice into a clean list
    # This turns "Step 1. Step 2." into a bulleted Markdown list
    formatted_advice = raw_advice.replace(". ", ".\n\n* ")
    if not formatted_advice.startswith("* "):
        formatted_advice = "* " + formatted_advice
    
    # Here I implemented Network Engineering Logic
    if loss > 1.0:
        status_label = "Degraded"
        reasoning = f"I've detected {round(loss, 2)}% packet loss. This often indicates congestion or hardware issues."
    elif lat > 100:
        status_label = "Lagging"
        reasoning = f"Your latency is currently high ({round(lat, 2)}ms)."
    elif bw < 20:
        status_label = "Slow"
        reasoning = "Your bandwidth speeds are below the expected threshold."
    else:
        status_label = "Healthy"
        reasoning = "Your network metrics are within optimal parameters."

    # This block Return the final intelligent response
    return {
        "status": "success",
        "status_label": status_label,  # Passed to Streamlit for sidebar colors
        "network_health": diagnostics,
        "answer": f"Analysis: **{status_label}**. {reasoning} \n\n### 📖 Expert Advice\n{formatted_advice}"
    }

# This is the Entry Point
if __name__ == "__main__":
    print("\n" + "="*40)
    print(" 🛰️  NETWORK COPILOT API IS STARTING...")
    print(" 🏠 Documentation: http://localhost:8000/docs")
    print("="*40 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)