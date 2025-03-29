from datetime import datetime
from flask import Flask, render_template, request, send_file
from func import init_db, insert_timestamp, insert_info, calc_duration, delete_timestamp, past_records_to_csv


app = Flask(__name__)

STAMP_DATES= {
    'start': None,
    'end': None,
    'break': None,
    'restart': None
    }

LAST_MINUTE_STAMP = ''


@app.route('/', methods=['GET', 'POST'])
def handle_stamp():
    today = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        data = request.get_json()
        stamp_value = data.get('stamp_value')
        # 同じ日に（取り消しボタン使用時を除き）2度同じボタンは押せない
        if STAMP_DATES[stamp_value] != today:
            insert_timestamp(stamp_value)
            STAMP_DATES[stamp_value] = today
            global LAST_MINUTE_STAMP 
            LAST_MINUTE_STAMP = stamp_value
            if stamp_value == 'start':
                insert_info()
            elif stamp_value == 'end':
                calc_duration()
    return render_template('index.html')


@app.route('/cancel', methods=['POST'])
def handle_cancel():
    delete_timestamp(LAST_MINUTE_STAMP)
    STAMP_DATES[LAST_MINUTE_STAMP] = None
    return render_template('index.html')


@app.route('/download_csv')
def download_csv():
    past_records_to_csv()
    return send_file('past_records.csv', as_attachment=True, mimetype='text/csv')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')