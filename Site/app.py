from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import pickle
import socket

app = Flask(__name__)
# set the secret key.  keep this really secret:
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
client = None

isDebug = False

@app.route("/", methods=['GET', 'POST'])
def home():
    global client
    if client is None:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((socket.gethostname(), 1214))
            print('Connected to server.')
        except Exception as e:
            print("Cannot connect to server.")
            flash('Connection Error.', category='error')
    return render_template('index.html')

@app.route("/search", methods=['POST'])
def search():
    if not isDebug:
        global client
        if request.method == 'POST':
            if client is None:
                flash('Connection Error.', category='error')
                print("Cannot connect to server.")
                return render_template("index.html")
            barkod = request.form['search']
            if not barkod.isdigit():
                flash('Barkod yalnızca sayı içerebilir.', category='error') 
                return render_template("index.html")
            message = "b"
            message += barkod
            message = message.encode('utf-8')
            client.send(message)
            
            # TODO : add ERROR handling
            from_server = client.recv(4096)
            from_server = from_server.decode('utf-8')
            print("From server : ",from_server)

            if from_server == "ERROR":
                flash('Barkod bulunamadı.', category='error')
                return render_template("index.html")

            # return render_template('test.html', test=from_server)
            data = pd.read_json(from_server)
        return render_template('result.html', barcodeno=data['barcodeno'][0], foodname=data['foodname'][0], brand=data['brand'][0], weightvolume=data['weightvolume'][0], ingredients=data['ingredients'][0], fat=data['fat'][0], protein=data['protein'][0], carbs=data['carbs'][0], calorie=data['calorie'][0], allergennames=data['allergennames'][0])
    else:
        from_server = "[{\"barcodeno\":1,\"foodname\":\"ekmek\",\"brand\":\"firinci\",\"weightvolume\":200,\"ingredients\":\"un\",\"fat\":20,\"protein\":10,\"carbs\":75,\"calorie\":300,\"allergennames\":\"['gluten', 'findik']\"}]"
        data = pd.read_json(from_server)
        return render_template('result.html', barcodeno=data['barcodeno'][0], foodname=data['foodname'][0], brand=data['brand'][0], weightvolume=data['weightvolume'][0], ingredients=data['ingredients'][0], fat=data['fat'][0], protein=data['protein'][0], carbs=data['carbs'][0], calorie=data['calorie'][0], allergennames=data['allergennames'][0])

@app.route("/signin")
def signin():
    return render_template('signin.html')

if __name__ == "__main__":
    app.run(debug=True)