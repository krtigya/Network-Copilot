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
    vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    vector_db = None
    print(" Warning: faiss_index folder not found. RAG features will be unavailable.")

# Here is the Function to store chat history with Debugging
def save_chat(user_query: str, ai_response: str):
    """Saves the conversation into the chat_history table in network_ops.db."""
    try:
        db_path = "data/network_ops.db"
        conn = sqlite3.connect(db_path)
        # We use a cursor to ensure the commit is handled correctly
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_query, ai_response) VALUES (?, ?)", 
            (user_query, ai_response)
        )
        conn.commit()
        conn.close()
        print(f" Chat saved to database: {user_query[:30]}...")
    except Exception as e:
        print(f" DATABASE SAVE ERROR: {e}")

def search_manuals(query: str):
    """Retrieves technical advice from FAISS vector index."""
    if not vector_db:
        return "Network manuals are currently offline."
    try:
        docs = vector_db.similarity_search(query, k=2)
        return " ".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"Troubleshooting step: Check hardware connections. (Error: {e})"

def get_network_diagnostics():
    try:
        db_path = "data/network_ops.db"
        if not os.path.exists(db_path):
            return {"error": "Database file not found."}
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM network_logs ORDER BY ROWID DESC LIMIT 1')
        row = cursor.fetchone()
        
        cursor.execute("PRAGMA table_info(network_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        return dict(zip(columns, row)) if row else {"message": "Table is empty."}
    except Exception as e:
        return {"error": str(e)}

# This is the API Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    diagnostics = get_network_diagnostics()
    
    # Here I Extract metrics 
    lat = diagnostics.get('latency_ms', 0)
    loss = diagnostics.get('packet_loss_rate', 0)
    bw = diagnostics.get('bandwidth_mbps', 0)
    
    # Here I UPDATE the Logic to handle live data queries vs RAG queries
    user_q = request.question.lower()
    if "ip" in user_q or "address" in user_q:
        advice_content = f"Your current Device IP address is recorded as: **{diagnostics.get('device_ip', 'Unknown')}**."
    else:
        raw_advice = search_manuals(request.question)
        # now co-pilot generates the Formatting advice into a list
        advice_content = raw_advice.replace(". ", ".\n\n* ")
        if not advice_content.startswith("* "):
            advice_content = "* " + advice_content
    
    # Engineering Logic to make the co-pilot  to label the network status
    if loss > 1.0:
        status_label = "Degraded"
        reasoning = f"I've detected {round(loss, 2)}% packet loss."
    elif lat > 100:
        status_label = "Lagging"
        reasoning = f"Your latency is high ({round(lat, 2)}ms)."
    elif bw < 20:
        status_label = "Slow"
        reasoning = "Bandwidth speeds are below expected thresholds."
    else:
        status_label = "Healthy"
        reasoning = "Network metrics are within optimal parameters."

    final_answer = f"Analysis: **{status_label}**. {reasoning} \n\n### Expert Advice\n{advice_content}"

    #this Saves to DB before returning the response
    save_chat(request.question, final_answer)

    return {
        "status": "success",
        "status_label": status_label,
        "network_health": diagnostics,
        "answer": final_answer
    }

if __name__ == "__main__":
    print("\n" + "="*40)
    print("NETWORK COPILOT API IS STARTING...")
    print("="*40 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)