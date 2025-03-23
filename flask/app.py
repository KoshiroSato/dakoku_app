from flask import Flask, render_template, request
from func import init_db, insert_timestamp

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stamp_value = request.form.get('stamp_value')
        insert_timestamp(stamp_value)
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')