from datetime import datetime
from flask import Flask, render_template, request
from func import init_db, insert_timestamp

app = Flask(__name__)

STAMP_DATES= {
    'start': None,
    'end': None,
    'break': None,
    'restart': None
    }

@app.route('/', methods=['GET', 'POST'])
def handle_stamp():
    today = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        data = request.get_json()
        stamp_value = data.get('stamp_value')
        # 同じ日に2度同じボタンは押せない
        if STAMP_DATES[stamp_value] != today:
            insert_timestamp(stamp_value)
            STAMP_DATES[stamp_value] = today
    return render_template('index.html')

@app.route('/cancel', methods=['POST'])
def handle_cancel():
    data = request.get_json()
    cancel_value = data.get('cancel_value')
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')