import sqlite3
import pandas as pd
import os

def import_traffic_to_sql(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    conn = sqlite3.connect("data/network_ops.db")
    df = pd.read_csv(csv_path)
    
    # 📝 Mapping your specific Kaggle columns to our DB schema
    column_mapping = {
        'latency': 'latency_ms',
        'bandwidth_usage': 'bandwidth_mbps',
        'packet_loss': 'packet_loss_rate',
        'jitter': 'jitter_ms',
        'traffic_type': 'status' 
    }
    
    try:
        # Select and rename
        df_filtered = df[list(column_mapping.keys())].copy()
        df_filtered.rename(columns=column_mapping, inplace=True)
        
        # Add a dummy device_ip since the CSV doesn't have one (for simulation)
        df_filtered['device_ip'] = "192.168.1.1"

        # Import top 1000 rows to the database
        df_filtered.head(1000).to_sql("network_logs", conn, if_exists="replace", index=False)
        print(f"✅ Success! Imported {len(df_filtered.head(1000))} rows with network metrics.")
        
    except Exception as e:
        print(f"❌ Mapping Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import_traffic_to_sql("data/network_traffic_dataset.csv")