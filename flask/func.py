import sqlite3

def init_db():
    conn = sqlite3.connect('stamp.db')
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