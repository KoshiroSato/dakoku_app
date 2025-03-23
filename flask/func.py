import os
import sqlite3
from datetime import datetime

def init_db():
    db_filename = 'stamp.db'

    if os.path.exists(db_filename):
        return
    
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS data (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              start TEXT,
              end TEXT,
              break TEXT,
              restart TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_timestamp(stamp_value):
    conn = sqlite3.connect('stamp.db')
    c = conn.cursor()

    current_time = datetime.now().isoformat()
    c.execute(f'INSERT INTO data ({stamp_value}) VALUES (?)', (current_time,))

    conn.commit()
    conn.close()