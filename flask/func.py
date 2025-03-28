import os, requests
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
              restart TEXT,
              duration INTEGER
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

def calc_duration():
    conn = sqlite3.connect('log.db')
    c = conn.cursor()

    c.execute('''
        UPDATE stamp
        SET duration = 
            (strftime('%s', end) - strftime('%s', start)) - 
            COALESCE((strftime('%s', restart) - strftime('%s', break)), 0)
        WHERE end IS NOT NULL AND start IS NOT NULL;
   ''')
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

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f'{hours}時間{minutes}分'

def past_records_to_csv():
    conn = sqlite3.connect('log.db')
    two_months_ago = datetime.now() - timedelta(days=60)
    two_months_ago_str = two_months_ago.strftime('%Y-%m-%d %H:%M:%S')
    df = pd.read_sql_query(
        'SELECT * FROM stamp WHERE start >= ? ORDER BY start ASC;',
        conn,
        params=(two_months_ago_str,)
    )
    datetime_cols = ['start', 'end', 'break', 'restart']
    df[datetime_cols] = df[datetime_cols].apply(pd.to_datetime)
    df[datetime_cols] = df[datetime_cols].apply(lambda x: x.dt.strftime('%Y年%m月%d日%H時%M分'))
    df['duration'] = df['duration'].map(format_duration)
    conn.close()
    df.to_csv('past_records.csv', index=False, encoding='utf-8')

def get_weather_info():
    try:
        jma_url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/110000.json'
        jma_json = requests.get(jma_url).json()    

        weather_code = jma_json[0]['timeSeries'][0]['areas'][0]['weatherCodes'][0]
        max_precip_avg = jma_json[1]['precipAverage']['areas'][0]['max']
        min_precip_avg = jma_json[1]['precipAverage']['areas'][0]['min']
        max_temp_avg = jma_json[1]['tempAverage']['areas'][0]['max']
        min_temp_avg = jma_json[1]['tempAverage']['areas'][0]['min']
        return weather_code, max_precip_avg, min_precip_avg, max_temp_avg, min_temp_avg
    except:
        return None, None, None, None, None