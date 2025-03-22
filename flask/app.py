from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        stamp_value = request.form.get('stamp_value')
        print(f"受け取った値: {stamp_value}")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')