import os
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document

load_dotenv()

#CONFIGURATION
KAGGLE_DATA_PATH = "data/customer_tickets.csv" # Path to your Kaggle dataset
DOCS_PATH = "docs/"
INDEX_SAVE_PATH = "faiss_index"

def load_local_docs():
    """Loads troubleshooting guides and manuals from the docs folder."""
    print(f"--- Loading local manuals from {DOCS_PATH} ---")
    loader = DirectoryLoader(
        path=DOCS_PATH,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()
    
    # Enrich metadata for local files
    for doc in docs:
        doc.metadata["source_type"] = "official_manual"
        
        doc.metadata["device_type"] = os.path.basename(doc.metadata["source"]).split('_')[0] # Tagging based on filename (e.g., 'zyxel_manual.txt' -> 'zyxel')
    
    return docs

def load_kaggle_data(file_path):
#Processes Kaggle CSV data into LangChain documents with Metadata Schema
    if not os.path.exists(file_path):
        print(f"WARNING: Kaggle file not found at {file_path}. Skipping.")
        return []

    print(f"--- Processing Kaggle Dataset: {file_path} ---")
    df = pd.read_csv(file_path)
    
    # Data Cleaning with Pandas
    # technical/network issues to maintain domain depth
    if 'Department' in df.columns:
        df = df[df['Department'].str.contains('Network|Technical|Support', na=False)]

    documents = []
    for _, row in df.head(100).iterrows(): # Limit to 100 for dev speed
        content = f"Ticket: {row.get('Subject', 'N/A')}\nDescription: {row.get('Body', '')}\nResolution: {row.get('Resolution', 'Pending')}"
        
        # Metadata Schema as per project requirements
        metadata = {
            "source_type": "historical_ticket",
            "issue_category": row.get('Tags', 'general'),
            "severity": row.get('Priority', 'low'),
            "device_type": "agnostic"
        }
        documents.append(Document(page_content=content, metadata=metadata))
    
    return documents

def split_semantically(documents):
    """Upgrades splitting from character-based to Semantic (Meaning-based)."""
    print("--- Performing Semantic Chunking ---")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Breakpoints are determined by changes in meaning, not character count
    splitter = SemanticChunker(
        embeddings, 
        breakpoint_threshold_type="percentile" 
    )
    
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} semantic chunks.")
    return chunks

def create_and_save_index(chunks):
    """Builds and persists the FAISS vector store."""
    print("--- Building FAISS Index ---")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_SAVE_PATH)
    print(f"Index saved successfully to {INDEX_SAVE_PATH}/")
    return vectorstore

def run_pipeline():
    #  Gather data from multiple sources
    manuals = load_local_docs()
    tickets = load_kaggle_data(KAGGLE_DATA_PATH)
    all_docs = manuals + tickets
    
    if not all_docs:
        print("Error: No data found to ingest.")
        return

    # Here, Process and Index
    chunks = split_semantically(all_docs)
    create_and_save_index(chunks)
    
    print("\n" + "="*30)
    print("INGESTION PIPELINE COMPLETE")
    print(f"Total Source Docs: {len(all_docs)}")
    print(f"Total Vector Chunks: {len(chunks)}")
    print("="*30)

if __name__ == "__main__":
    run_pipeline()