import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
from flask_apscheduler import APScheduler
from module import DatabaseManager, StampManager, InfoManager
from ml import CreateDataset, MLModel


STAMP_DATES= {
    'start': None,
    'end': None,
    'break': None,
    'restart': None
    }


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
scheduler = APScheduler()

# my module
db_manager = DatabaseManager()
stamp_manager = StampManager(db_manager)
info_manager = InfoManager(db_manager)
ml_model = MLModel(stamp_manager, CreateDataset)

# 機械学習モデルの訓練スケジューラー
scheduler.add_job(
    id='daily_task', 
    func=ml_model.fitting, 
    trigger='cron',
    hour=0, 
    minute=0
    )
scheduler.init_app(app)
scheduler.start()

db_manager.init_db()


@app.route('/', methods=['GET', 'POST'])
def handle_stamp():
    today = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        data = request.get_json()
        stamp_value = data.get('stamp_value')
        # 出勤ボタンを押さずに他のボタンを押せないようにする
        if stamp_value in ['break', 'restart', 'end'] and STAMP_DATES['start'] == None:
            return render_template('index.html')
        # 中断ボタンを押さずに再開ボタンを押せないようにする
        elif stamp_value == 'restart' and STAMP_DATES['break'] == None:
            return render_template('index.html')
        else:
            # 同じ日に（取り消しボタン使用時を除き）2度同じボタンは押せない
            if STAMP_DATES[stamp_value] != today:
                stamp_manager.insert_timestamp(stamp_value)
                STAMP_DATES[stamp_value] = today
                session['just_before_stamp'] = stamp_value
                if stamp_value == 'start':
                    info_manager.insert_info()
                elif stamp_value == 'end':
                    stamp_manager.calc_working_time()
    return render_template('index.html')


@app.route('/cancel', methods=['POST'])
def handle_cancel():
    just_before_stamp = session.get('just_before_stamp')
    if just_before_stamp:
        stamp_manager.delete_timestamp(just_before_stamp)
        STAMP_DATES[just_before_stamp] = None
        if just_before_stamp == 'start':
            info_manager.delete_info()
        session.pop('just_before_stamp', None)
    return render_template('index.html')


@app.route('/predict')
def ml_predict():
    db_length = stamp_manager.get_record_length()
    if db_length >= 90 and os.path.exists('output/model.pkl'):
        pred = ml_model.predict()
        pred = f'本日の予想退勤時間は{pred}です。'
    else:
        pred = '今日も1日頑張りましょう。'
    flash(pred, 'pred')  
    return redirect(url_for('handle_stamp'))  


@app.route('/download_csv')
def download_csv():
    stamp_manager.past_records_to_csv()
    return send_file('output/past_records.csv', as_attachment=True, mimetype='text/csv')