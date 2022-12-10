from flask import Flask, render_template, request, redirect, url_for, flash

import pickle
import socket

app = Flask(__name__)
# set the secret key.  keep this really secret:
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/", methods=['GET', 'POST'])
def home():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((socket.gethostname(), 1234))
        print('Connected to server.')
    except Exception as e:
        flash('Connection Error.', category='error')
        return render_template('index.html')

    message = "Gökalpten selamlar"
    message = message.encode('utf-8')
    client.send(message)
    from_server = client.recv(4096)
    from_server = from_server.decode('utf-8')
    print("From server : ",from_server)
    client.close()
    return render_template('index.html')

@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        search = request.form['search']
        return render_template('test.html', test=search)

@app.route("/signin")
def signin():
    return render_template('signin.html')

if __name__ == "__main__":
    app.run(debug=True)