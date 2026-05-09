import sqlite3
import os

# Path to the database from the root directory
db_path = 'data/network_ops.db'

# Connect and create the table
conn = sqlite3.connect(db_path)
conn.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        role TEXT, 
        content TEXT, 
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.close()

print(f" Chat history table initialized at {db_path}")