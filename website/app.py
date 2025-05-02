from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/donations')
def donats():
    return render_template('donations.html')