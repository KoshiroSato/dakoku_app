import os
import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from utils import format_leave_time


class DatabaseManager:
    '''
    SQLiteとの接続、テーブルの初期化
    '''
    def __init__(self):
        self.db_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.db')

    def get_connection(self):
        return sqlite3.connect(self.db_filename)

    def init_db(self):
        '''
        打刻情報を管理するstampテーブルと機械学習のための
        日時付加情報を管理するinfoテーブルの作成
        '''
        if os.path.exists(self.db_filename):
            return

        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE stamp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start TEXT,
                    end TEXT,
                    break TEXT,
                    restart TEXT,
                    working_time INTEGER
                )
            ''')
            c.execute('''
                CREATE TABLE info (
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


class StampManager:
    '''
    打刻や勤務時間の計算、CSV出力などを担当
    '''
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def insert_timestamp(self, stamp_value):
        with self.db_manager.get_connection() as conn:
            c = conn.cursor()
            current_time = datetime.now().isoformat()
            # 空のレコードの中で最も大きなIDを探す
            c.execute(f'''
                SELECT id FROM stamp 
                WHERE {stamp_value} IS NULL OR {stamp_value} = ''
                ORDER BY id DESC LIMIT 1
            ''')
            row = c.fetchone()
            if row:
                # 最も大きなIDにデータを入れる
                c.execute(f'UPDATE stamp SET {stamp_value} = ? WHERE id = ?', (current_time, row[0]))
            else:
                # 空のレコードがなければ、新規INSERT
                c.execute(f'INSERT INTO stamp ({stamp_value}) VALUES (?)', (current_time,))

    def delete_timestamp(self, stamp_value):
        with self.db_manager.get_connection() as conn:
            c = conn.cursor()
            c.execute(f'''
                UPDATE stamp SET {stamp_value} = NULL 
                WHERE id = (SELECT MAX(id) FROM stamp)
            ''')

    def calc_working_time(self):
        '''
        秒単位で勤務時間を計算
        '''
        with self.db_manager.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE stamp
                SET working_time = 
                    (strftime('%s', end) - strftime('%s', start)) - 
                    COALESCE((strftime('%s', restart) - strftime('%s', break)), 0)
                WHERE end IS NOT NULL AND start IS NOT NULL;
            ''')

    def get_record_length(self):
        with self.db_manager.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM stamp')
            return c.fetchone()[0]

    def past_records_to_csv(self):
        '''
        過去60日分の打刻情報をCSVでエクスポート
        '''
        with self.db_manager.get_connection() as conn:
            two_months_ago = datetime.now() - timedelta(days=60)
            df = pd.read_sql_query(
                'SELECT * FROM stamp WHERE start >= ? ORDER BY start ASC;',
                conn,
                params=(two_months_ago.strftime('%Y-%m-%d %H:%M:%S'),)
            )

        df[['start', 'end', 'break', 'restart']] = df[['start', 'end', 'break', 'restart']].apply(pd.to_datetime)
        # 年と月日と時刻を分離して格納する
        df['year'] = df['start'].dt.strftime('%Y年')
        df['month'] = df['start'].dt.strftime('%m月%d日')
        df[['start', 'end', 'break', 'restart']] = df[['start', 'end', 'break', 'restart']].apply(lambda x: x.dt.strftime('%H時%M分'))
        df['working_time'] = df['working_time'].map(lambda s: f"{s // 3600}時間{s % 3600 // 60}分")
        df.drop(columns=['id'], inplace=True)
        df = df[['year', 'month', 'start', 'end', 'break', 'restart', 'working_time']]
        df.to_csv('output/past_records.csv', index=False, encoding='utf-8')


class InfoManager:
    '''
    天気と日付情報を取得し、保存
    '''
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def insert_info(self):
        with self.db_manager.get_connection() as conn:
            c = conn.cursor()
            info_data = {**self.get_weather_info(), **self.get_date_info()}
            columns = ', '.join(info_data.keys())
            values = tuple(info_data.values())
            placeholders = ', '.join(['?'] * len(info_data))
            c.execute(f'INSERT INTO info ({columns}) VALUES ({placeholders})', values)

    def delete_info(self):
        '''
        startの打刻を取り消した場合の処理
        '''
        with self.db_manager.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM info WHERE id = (SELECT MAX(id) FROM info)')

    def get_weather_info(self):
        try:
            jma_url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/110000.json'
            jma_json = requests.get(jma_url).json()
            return {
                'weather_code': int(jma_json[0]['timeSeries'][0]['areas'][0]['weatherCodes'][0]),
                'max_precip_avg': float(jma_json[1]['precipAverage']['areas'][0]['max']),
                'min_precip_avg': float(jma_json[1]['precipAverage']['areas'][0]['min']),
                'max_temp_avg': float(jma_json[1]['tempAverage']['areas'][0]['max']),
                'min_temp_avg': float(jma_json[1]['tempAverage']['areas'][0]['min']),
            }
        except:
            return dict.fromkeys([
                'weather_code', 'max_precip_avg', 'min_precip_avg', 'max_temp_avg', 'min_temp_avg'
            ], None)

    def get_date_info(self):
        today = datetime.today()
        season = ('Winter', 'Spring', 'Summer', 'Autumn')[(today.month % 12) // 3]
        return {
            'month': today.month,
            'day': today.day,
            'weekday': today.strftime('%A'),
            'season': season
        }