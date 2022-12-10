from flask import Flask, render_template, request, redirect, url_for, flash

import pickle
import socket

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        search = request.form['search']
        return render_template('test.html', test=search)

if __name__ == "__main__":
    app.run(debug=True)