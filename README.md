# Network Copilot: AI-Powered Telemetry Agent

An intelligent network monitoring system that combines real-time data analysis with expert troubleshooting advice.This project combines SQL-based telemetry analysis with Retrieval-Augmented Generation (RAG) using FAISS.

## The System Architecture
This project implements a **Compound AI System** using two primary data brains:
1.  **Operational Brain (SQL):** Queries live telemetry (Latency, Bandwidth, Packet Loss) from a SQLite database.
2.  **Knowledge Brain (RAG):** Uses a **FAISS** vector index to retrieve specific troubleshooting steps from technical manuals.

## Features
*   **Real-Time Diagnostics:** Analyzes metrics to classify network health as "Healthy," "Lagging," or "Degraded".
*   **Expert Advice:** Automatically provides technical solutions based on the current network status.
*   **Interactive Dashboard:** Built with Streamlit, featuring live charts, manual refresh, and PDF/Text report exports.

## This is the Project Structure
```text
├── data/               # Network telemetry database (network_ops.db)
├── faiss_index/        # Vector database for expert manuals
├── src/
│   ├── api/main.py     # FastAPI backend & Reasoning engine
│   └── ui/app.py       # Streamlit frontend
├── docker/             # Dockerization files
└── requirements.txt    # Project dependencies