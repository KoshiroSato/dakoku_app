import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def init_db():
    db_filename = 'log.db'

    if os.path.exists(db_filename):
        return
    
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS stamp (
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
    conn = sqlite3.connect('log.db')
    c = conn.cursor()

    current_time = datetime.now().isoformat()
    # 空のレコードを探す
    c.execute(
        f"SELECT id FROM stamp WHERE {stamp_value} IS NULL OR {stamp_value} = '' ORDER BY id LIMIT 1"
        )
    row = c.fetchone()
    
    if row:
        # 空のレコードがあれば、そのIDにデータを入れる
        empty_id = row[0]
        c.execute(f'UPDATE stamp SET {stamp_value} = ? WHERE id = ?', (current_time, empty_id))
    else:
        # 空のレコードがなければ、新規INSERT
        c.execute(f'INSERT INTO stamp ({stamp_value}) VALUES (?)', (current_time,))

    conn.commit()
    conn.close()

def delete_timestamp(stamp_value):
    conn = sqlite3.connect('log.db')
    c = conn.cursor()
    c.execute(
        f'UPDATE stamp SET {stamp_value} = NULL WHERE id = (SELECT MAX(id) FROM stamp)'
        )
    conn.commit()
    conn.close()

def past_records_to_csv():
    conn = sqlite3.connect('log.db')
    two_months_ago = datetime.now() - timedelta(days=60)
    two_months_ago_str = two_months_ago.strftime('%Y-%m-%d %H:%M:%S')
    df = pd.read_sql_query(
        'SELECT * FROM stamp WHERE start >= ? ORDER BY start ASC;',
        conn,
        params=(two_months_ago_str,)
    )
    conn.close()
    df.to_csv('past_records.csv', index=False, encoding='utf-8')
