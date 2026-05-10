# Network Copilot

## Overview

Network Copilot is an AI-powered network monitoring system that combines real-time telemetry analysis with intelligent troubleshooting advice. It allows network operators and engineers to query the health of their network in plain English and receive structured, data-driven responses.

The system reads live network metrics from a database, classifies the current network state, and uses a retrieval-augmented generation pipeline to provide relevant technical guidance from a historical knowledge base.

---

## How It Works

The system is built around two intelligence layers that work together on every request.

The first layer is the Operational Brain. It queries a SQLite database containing live network telemetry including latency, bandwidth, and packet loss. It uses this data to classify the current network status as Healthy, Lagging, Degraded, or Slow based on defined thresholds.

The second layer is the Knowledge Brain. It uses a FAISS vector index built from thousands of historical IT support tickets. When a question is asked, the system searches this index for the most relevant troubleshooting steps and includes them in the response.

Both layers are combined into a single answer returned through the API and displayed in the dashboard.

---

## Features

- Real-time network diagnostics based on live telemetry data
- Natural language chat interface to query network status
- Automatic health classification with defined thresholds
- Expert troubleshooting advice retrieved from a historical knowledge base
- Persistent chat history stored in the database across sessions
- Downloadable diagnostic report from the dashboard
- REST API for integration with external tools
- Fully containerized with Docker for easy deployment

---

## Project Structure

    Network-Copilot/
    |
    |-- data/
    |   |-- network_ops.db              SQLite database for logs and chat history
    |   |-- network_traffic_dataset.csv Source data for network metrics
    |   |-- IT Support Ticket Data.csv  Source data for the knowledge base
    |
    |-- faiss_index/                    Vector index built from support tickets
    |
    |-- src/
    |   |-- api/
    |   |   |-- main.py                 FastAPI backend and reasoning engine
    |   |
    |   |-- core/
    |   |   |-- database.py             Database initialization
    |   |   |-- import_metrics.py       Imports CSV data into the database
    |   |   |-- ingest.py               Loads documents for vector indexing
    |   |   |-- populate_logs.py        Populates sample network logs
    |   |
    |   |-- ui/
    |   |   |-- app.py                  Streamlit frontend dashboard
    |   |
    |   |-- simulate_traffic.py         Simulates live network traffic every 5 seconds
    |   |-- init_db.py                  Initializes the database schema
    |
    |-- docker/
    |   |-- dockerfile                  Docker image definition
    |
    |-- docker-compose.yml              Runs backend and frontend together
    |-- requirements.txt                Python dependencies

---

## Technology Stack

- Backend API: FastAPI with Uvicorn
- Frontend Dashboard: Streamlit
- Database: SQLite
- Vector Search: FAISS
- Embeddings: HuggingFace all-MiniLM-L6-v2 via sentence-transformers
- AI Framework: LangChain
- Containerization: Docker and Docker Compose

---

## Network Health Thresholds

The system uses the following rules to classify network health:

    Packet Loss above 1.0%       -> Degraded
    Latency above 100ms          -> Lagging
    Bandwidth below 20 Mbps      -> Slow
    All metrics within range     -> Healthy

---

## Setup and Installation

### Option 1 - Docker (Recommended)

Requires Docker and Docker Compose installed on the machine.

    docker compose up --build

This starts two services:

    Backend API   ->  http://localhost:8000
    Frontend UI   ->  http://localhost:8501

### Option 2 - Local (Development)

Requires Python 3.11 or later.

Step 1. Create and activate a virtual environment:

    python -m venv .venv
    source .venv/bin/activate

Step 2. Install dependencies:

    pip install -r requirements.txt

Step 3. Initialize the database:

    python src/init_db.py

Step 4. Import network metrics into the database:

    python src/core/import_metrics.py

Step 5. Build the FAISS knowledge index (one-time setup):

    python -c "
    import pandas as pd
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.document_loaders import DataFrameLoader

    df = pd.read_csv('data/IT Support Ticket Data.csv')
    df = df.dropna(subset=['Body'])
    loader = DataFrameLoader(df, page_content_column='Body')
    docs = loader.load()
    embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
    db = FAISS.from_documents(docs, embeddings)
    db.save_local('faiss_index')
    print('Knowledge base ready.')
    "

Step 6. Start the backend (Terminal 1):

    python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

Step 7. Start the frontend (Terminal 2):

    streamlit run src/ui/app.py

Step 8. Start the traffic simulator to generate live data (Terminal 3):

    python src/simulate_traffic.py

---

## Using the System

Once running, open http://localhost:8501 in a browser.

The dashboard displays three live metric tiles showing current latency, bandwidth, and packet loss. The sidebar shows the overall network status and a button to refresh the telemetry feed. A diagnostic report can be downloaded from the sidebar at any time.

The chat interface at the bottom of the page accepts natural language questions such as:

    How is my network performing?
    Why is my latency high?
    What is my IP address?
    What should I do about packet loss?

Every conversation is saved to the database and persists across page reloads.

---

## API Reference

The backend exposes a single endpoint for all queries.

    POST /chat

Request body:

    {
        "question": "How is my network?"
    }

Response:

    {
        "status": "success",
        "status_label": "Healthy",
        "network_health": {
            "latency_ms": 22.0,
            "bandwidth_mbps": 90.64,
            "packet_loss_rate": 0.13,
            "device_ip": "192.168.1.1",
            "status": "Online"
        },
        "answer": "Analysis: Healthy. Network metrics are within optimal parameters. ..."
    }

Interactive API documentation is available at http://localhost:8000/docs while the backend is running.

---

## Database Schema

The database contains two tables.

network_logs stores the telemetry readings:

    latency_ms         Latency in milliseconds
    bandwidth_mbps     Bandwidth in megabits per second
    packet_loss_rate   Packet loss as a percentage
    jitter_ms          Jitter in milliseconds
    status             Online, Offline, or High Latency
    device_ip          IP address of the monitored device

chat_history stores all conversations:

    session_id         Session identifier
    user_query         The question asked by the user
    ai_response        The full response returned by the system
    timestamp          Time the message was recorded
