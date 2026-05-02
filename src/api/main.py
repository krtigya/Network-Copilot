import sqlite3
import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Network Copilot API")

# Define Request/Response Models
class ChatRequest(BaseModel):
    question: str

# The Diagnostic Tool (Your SQL logic)
def get_network_diagnostics(device_ip: str = "192.168.1.1"):
    try:
        db_path = "data/network_ops.db"
        if not os.path.exists(db_path):
            return {"error": "Database file not found."}
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 💡 FIX: Use ROWID instead of 'id' since it exists by default
        cursor.execute('SELECT * FROM network_logs ORDER BY ROWID DESC LIMIT 1')
        row = cursor.fetchone()
        
        cursor.execute("PRAGMA table_info(network_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        if row:
            return dict(zip(columns, row))
            
        return {"message": "Table is empty."}
    except Exception as e:
        print(f"❌ DATABASE CRASH: {e}")
        return {"error": str(e)}
#  The API Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    diagnostics = get_network_diagnostics()
    
    # Check if diagnostics is a dictionary (success) or a string/error
    if isinstance(diagnostics, dict) and "error" not in diagnostics:
        status = diagnostics.get('status', 'Active')
        latency = diagnostics.get('latency_ms', diagnostics.get('latency', 'N/A'))
        answer = f"I've analyzed your connection. Current status is {status} with {latency} latency."
    else:
        answer = "I'm having trouble accessing your real-time network logs right now."
    
    return {
        "status": "success" if "error" not in diagnostics else "error",
        "data_source": "SQL_Database",
        "network_health": diagnostics,
        "answer": answer
    }

# The Correct Entry Point (Fixed Typos)
if __name__ == "__main__":
    print("\n" + "="*40)
    print(" NETWORK COPILOT API IS STARTING...")
    print(" Access at: http://localhost:8000/docs")
    print("="*40 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)