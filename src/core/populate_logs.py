import sqlite3
import random
import time

def simulate_live_traffic():
    conn = sqlite3.connect("data/network_ops.db")
    cursor = conn.cursor()
    
    statuses = ['Online', 'Online', 'Online', 'High Latency', 'Offline']
    
    print("Simulating live network traffic... (Press Ctrl+C to stop)")
    try:
        while True:
            customer_id = f"CUST_{random.randint(1000, 9999)}"
            status = random.choice(statuses)
            latency = random.randint(10, 150) if status != 'Offline' else 0
            bandwidth = round(random.uniform(1.0, 100.0), 2) if status == 'Online' else 0.0
            
            cursor.execute('''
                INSERT INTO network_logs (customer_id, device_ip, status, latency_ms, bandwidth_mbps)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer_id, "192.168.1.1", status, latency, bandwidth))
            
            conn.commit()
            time.sleep(5) 
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    simulate_live_traffic()