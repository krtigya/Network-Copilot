import pandas as pd
from langchain_community.document_loaders import DataFrameLoader

def load_csv_data(file_path, content_column):
    """Loads specific columns from your Kaggle CSVs for the Vector Store."""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # We focus on columns like 'Ticket Description' or 'Resolution'
        loader = DataFrameLoader(df, page_content_column=content_column)
        return loader.load()
    return []

# Usage during ingestion:
# tickets = load_csv_data("data/IT Support Ticket Data.csv", "Ticket Description")