import sqlite3
import random
import time
import os

def simulate_live_traffic():
    db_path = "data/network_ops.db"
    
    if not os.path.exists(db_path):
        print(f" Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    statuses = ['Online', 'Online', 'Online', 'High Latency', 'Offline']
    
    print("Network Traffic Simulation Started...")
    print("Please!! Press Ctrl+C to stop the simulation.")
    
    try:
        while True:
            status = random.choice(statuses)
            
            # Logic: Assign values based on the random status
            if status == 'Online':
                latency = random.randint(10, 40)
                bandwidth = round(random.uniform(50.0, 100.0), 2)
                packet_loss = round(random.uniform(0.0, 0.5), 2)
            elif status == 'High Latency':
                latency = random.randint(120, 300)
                bandwidth = round(random.uniform(5.0, 20.0), 2)
                packet_loss = round(random.uniform(0.6, 2.0), 2)
            else: # Offline
                latency = 0
                bandwidth = 0.0
                packet_loss = 0.0

            # 🛠️ MATCHING YOUR SCHEMA: We only use columns that exist in your DB
            # We removed customer_id here.
            cursor.execute('''
                INSERT INTO network_logs (device_ip, status, latency_ms, bandwidth_mbps, packet_loss_rate)
                VALUES (?, ?, ?, ?, ?)
            ''', ("192.168.1.1", status, latency, bandwidth, packet_loss))
            
            conn.commit()
            print(f"Log Added: {status} | Latency: {latency}ms | BW: {bandwidth}Mbps")
            
            time.sleep(5) 
            
    except KeyboardInterrupt:
        print("\n Simulation stopped.")
    except sqlite3.OperationalError as e:
        print(f" Database Error: {e}")
        print(" If there is error then tip is that"
        " Check your table column names in VS Code SQLite Explorer.")
    finally:
        conn.close()

if __name__ == "__main__":
    simulate_live_traffic()