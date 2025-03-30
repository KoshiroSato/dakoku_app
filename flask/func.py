import os, requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta


config = {
    'db_filename': 'log.db',
}


def get_db_connection(config=config):
    return sqlite3.connect(config['db_filename'])


def init_db(config=config):
    '''
    打刻情報を管理するstampテーブルと機械学習のための
    日時付加情報を管理するinfoテーブルの作成
    '''
    if os.path.exists(config['db_filename']):
        return
    
    with get_db_connection() as conn:
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

        c.execute('''
            CREATE TABLE IF NOT EXISTS info (
                id INTEGER PRIMARY KEY,
                month NUMERIC,
                day NUMERIC,
                weekday TEXT,
                season TEXT,
                weather_code NUMERIC,
                max_precip_avg REAL,
                min_precip_avg REAL,
                max_temp_avg REAL,
                min_temp_avg REAL
            ) 
    ''')


def insert_timestamp(stamp_value):
    with get_db_connection() as conn:
        c = conn.cursor()

        current_time = datetime.now().isoformat()

        # 空のレコードの中で最も大きなIDを探す
        c.execute(f"""
            SELECT id FROM stamp 
            WHERE {stamp_value} IS NULL OR {stamp_value} = ''
            ORDER BY id DESC LIMIT 1
        """)
        row = c.fetchone()

        if row:
            # 最も大きなIDにデータを入れる
            empty_id = row[0]
            c.execute(f'UPDATE stamp SET {stamp_value} = ? WHERE id = ?', (current_time, empty_id))
        else:
            # 空のレコードがなければ、新規INSERT
            c.execute(f'INSERT INTO stamp ({stamp_value}) VALUES (?)', (current_time,))


def insert_info():
    with get_db_connection() as conn:
        c = conn.cursor()
        weather_info = get_weather_info()
        date_info = get_date_info()
        info_data = {**weather_info, **date_info}
        columns = ', '.join(info_data.keys())
        values = tuple(info_data.values())
        place_holders = ', '.join(['?' for _ in info_data])
        c.execute(f'INSERT INTO info ({columns}) VALUES ({place_holders})', values)


def delete_info():
    '''
    startの打刻を取り消した場合の処理
    '''
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM info WHERE id = (SELECT MAX(id) FROM info)')


def calc_duration():
    '''
    秒単位で勤務時間を計算
    '''
    with get_db_connection() as conn:
        c = conn.cursor()

        c.execute('''
            UPDATE stamp
            SET duration = 
                (strftime('%s', end) - strftime('%s', start)) - 
                COALESCE((strftime('%s', restart) - strftime('%s', break)), 0)
            WHERE end IS NOT NULL AND start IS NOT NULL;
        ''')


def delete_timestamp(stamp_value):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(
            f'UPDATE stamp SET {stamp_value} = NULL WHERE id = (SELECT MAX(id) FROM stamp)'
            )


def past_records_to_csv():
    '''
    過去60日分の打刻情報をCSVでエクスポート
    '''
    def format_duration(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f'{hours}時間{minutes}分'
    
    with get_db_connection() as conn:
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
    df.to_csv('past_records.csv', index=False, encoding='utf-8')


def get_weather_info():
    try:
        jma_url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/110000.json'
        jma_json = requests.get(jma_url).json()

        weather_code = int(jma_json[0]['timeSeries'][0]['areas'][0]['weatherCodes'][0])
        max_precip_avg = float(jma_json[1]['precipAverage']['areas'][0]['max'])
        min_precip_avg = float(jma_json[1]['precipAverage']['areas'][0]['min'])
        max_temp_avg = float(jma_json[1]['tempAverage']['areas'][0]['max'])
        min_temp_avg = float(jma_json[1]['tempAverage']['areas'][0]['min'])
        return {
            'weather_code': weather_code, 
            'max_precip_avg': max_precip_avg, 
            'min_precip_avg': min_precip_avg, 
            'max_temp_avg': max_temp_avg, 
            'min_temp_avg': min_temp_avg
            }
    except:
        return {
            'weather_code': None, 
            'max_precip_avg': None, 
            'min_precip_avg': None, 
            'max_temp_avg': None, 
            'min_temp_avg': None
            }
    

def get_date_info():
    today = datetime.today()

    month = today.month
    day = today.day
    weekday = today.strftime('%A')

    if month in [3, 4, 5]:
        season = 'Spring'
    elif month in [6, 7, 8]:
        season = 'Summer'
    elif month in [9, 10, 11]:
        season = 'Autumn'
    else:
        season = 'Winter'
    return {'month': month, 'day': day, 'weekday': weekday, 'season': season}