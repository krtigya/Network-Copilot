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
            # We add a 'Slow' and 'Laggy' choice to the random selector
            status = random.choice(['Online', 'High Latency', 'Low Bandwidth', 'Congested'])
            
            if status == 'Online':
                latency = random.randint(10, 40)
                bandwidth = round(random.uniform(70.0, 100.0), 2)
                packet_loss = round(random.uniform(0.0, 0.3), 2)
                
            elif status == 'High Latency':
                latency = random.randint(150, 400) 
                bandwidth = round(random.uniform(40.0, 60.0), 2)
                packet_loss = round(random.uniform(0.0, 0.4), 2) 
                
            elif status == 'Low Bandwidth':
                latency = random.randint(20, 50)
                bandwidth = round(random.uniform(1.0, 15.0), 2)
                packet_loss = round(random.uniform(0.0, 0.2), 2)
                
            else:
                latency = random.randint(60, 100)
                bandwidth = round(random.uniform(20.0, 40.0), 2)
                packet_loss = round(random.uniform(1.5, 5.0), 2)

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