import os
from datetime import datetime
from flask import Flask, render_template, request, send_file
from flask_apscheduler import APScheduler
from func import init_db, insert_timestamp, insert_info, delete_info, calc_working_time, delete_timestamp, get_record_length, past_records_to_csv
from ml import model_fitting, model_predict


STAMP_DATES= {
    'start': None,
    'end': None,
    'break': None,
    'restart': None
    }

LAST_MINUTE_STAMP = ''


app = Flask(__name__)
scheduler = APScheduler()

# 機械学習モデルの訓練スケジューラー
scheduler.add_job(
    id='daily_task', 
    func=model_fitting, 
    trigger='cron',
    hour=0, 
    minute=0
    )
scheduler.init_app(app)
scheduler.start()


@app.route('/', methods=['GET', 'POST'])
def handle_stamp():
    today = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        data = request.get_json()
        stamp_value = data.get('stamp_value')
        # 出勤ボタンを押さずに他のボタンを押せないようにする
        if stamp_value in ['break', 'restart', 'end'] and STAMP_DATES['start'] == None:
            pass
        # 中断ボタンを押さずに再開ボタンを押せないようにする
        elif stamp_value == 'restart' and STAMP_DATES['break'] == None:
            pass
        else:
            # 同じ日に（取り消しボタン使用時を除き）2度同じボタンは押せない
            if STAMP_DATES[stamp_value] != today:
                insert_timestamp(stamp_value)
                STAMP_DATES[stamp_value] = today
                global LAST_MINUTE_STAMP 
                LAST_MINUTE_STAMP = stamp_value
                if stamp_value == 'start':
                    insert_info()
                    db_length = get_record_length()
                    if db_length >= 90 and os.path.exists('output.model.pkl'):
                        pred = model_predict()
                elif stamp_value == 'end':
                    calc_working_time()
    return render_template('index.html')


@app.route('/cancel', methods=['POST'])
def handle_cancel():
    delete_timestamp(LAST_MINUTE_STAMP)
    STAMP_DATES[LAST_MINUTE_STAMP] = None
    if LAST_MINUTE_STAMP == 'start':
        delete_info()
    return render_template('index.html')


@app.route('/download_csv')
def download_csv():
    past_records_to_csv()
    return send_file('output/past_records.csv', as_attachment=True, mimetype='text/csv')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')