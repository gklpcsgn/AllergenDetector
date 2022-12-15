from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import pandas as pd
import pickle
import socket
import json

app = Flask(__name__)
# set the secret key.  keep this really secret:
app.secret_key = b'talha'
client = None

# all_allergens = None

login_manager = LoginManager()
login_manager.init_app(app)

isDebug = False

try:
    f = open("debugEnabled", "r")
    isDebug = True
    f.close()
except:
    isDebug = False

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class User(UserMixin):
    def __init__(self,userid , personname,personsurname,username,telephoneno=None,height=None,weight=None,allergens=None,is_admin=False):
        self.username = username
        self.personname = personname
        self.personsurname = personsurname
        self.telephoneno = telephoneno
        self.id = userid
        self.weight = weight
        self.height = height
        self.is_admin = is_admin
        self.allergens = None

    def set_allergens(self,allergens):
        self.allergens = allergens

    def __repr__(self):
        return f"User('{self.id}',{self.username}', '{self.personname}', '{self.personsurname}')"
    def get_id(self):
        return self.id

    
    def get_by_id(userid):
        global client
        if client is None:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((socket.gethostname(), 1214))
                print('Connected to server.')
            except Exception as e:
                print("Cannot connect to server.")
                flash('Connection Error.', category='error')
        message = "a"
        message += str(userid)
        message = message.encode('utf-8')
        client.send(message)

        from_server = client.recv(4096)
        from_server = from_server.decode('utf-8')

        

        if from_server == "ERRORAUTHENTICATION":
            return None
        else:
            user_data = pd.read_json(from_server)
            u =  User(user_data['userid'][0], user_data['personname'][0], user_data['personsurname'][0], user_data['e_mail'][0], user_data['telephoneno'][0], user_data['height'][0], user_data['weight'][0], is_admin=user_data['is_admin'][0])
            return u
            


@app.route("/", methods=['GET', 'POST'])
def home():
    global client
    if not isDebug:
        if client is None:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((socket.gethostname(), 1214))
                print('Connected to server.')
            except Exception as e:
                print("Cannot connect to server.")
                flash('Connection Error.', category='error')
    else:
        flash('Debug mode enabled.')
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
            message += str(barkod)
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
            allergens = data["allergennames"][0].replace("'","\"")
            allergens = json.loads(allergens)
            print("allergens : ", allergens)
            return render_template('result.html', barcodeno=data['barcodeno'][0], foodname=data['foodname'][0], brand=data['brand'][0], weightvolume=data['weightvolume'][0], ingredients=data['ingredients'][0], fat=data['fat'][0], protein=data['protein'][0], carbs=data['carbs'][0], calorie=data['calorie'][0], allergens=allergens)
    else:
        from_server = "[{\"barcodeno\":1,\"foodname\":\"ekmek\",\"brand\":\"firinci\",\"weightvolume\":200,\"ingredients\":\"un\",\"fat\":20,\"protein\":10,\"carbs\":75,\"calorie\":300,\"allergennames\":\"['gluten', 'findik']\"}]"
        data = pd.read_json(from_server)
        allergens = data["allergennames"][0].replace("'","\"")
        allergens = json.loads(allergens)
        return render_template('result.html', barcodeno=data['barcodeno'][0], foodname=data['foodname'][0], brand=data['brand'][0], weightvolume=data['weightvolume'][0], ingredients=data['ingredients'][0], fat=data['fat'][0], protein=data['protein'][0], carbs=data['carbs'][0], calorie=data['calorie'][0], allergens=allergens)

@app.route("/searchName", methods=['POST'])
def searchName():
    global isDebug
    if not isDebug:
        global client
        if request.method == 'POST':
            if client is None:
                flash('Connection Error.', category='error')
                print("Cannot connect to server.")
                return render_template("index.html")
            foodname = request.form['searchName']
            message = "s"
            message += foodname
            message = message.encode('utf-8')
            client.send(message)
            
            # TODO : add ERROR handling
            from_server = client.recv(4096)
            from_server = from_server.decode('utf-8')
            print("From server : ",from_server)

            if from_server == "ERROR":
                flash('Ürün adı bulunamadı.', category='error')
                return render_template("name_search.html")

            # return render_template('test.html', test=from_server)
            data = pd.read_json(from_server)
            return render_template('search_results.html', data=data)
    else:
        from_server = '[{\"barcodeno\":1,\"brand\":\"firinci\",\"foodname\":\"ekmek\"},{\"barcodeno\":2,\"brand\":\"Eti\",\"foodname\":\"kek\"}]'
        data = pd.read_json(from_server)
        return render_template('search_results.html', data=data)

@app.route("/name_search")
def searchbyname():
    return render_template('name_search.html')

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    global client
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        # session.pop('username', None)
        if client is None:
            flash('Connection Error.', category='error')
            print("Cannot connect to server.")
            return render_template("index.html")
        # send username and password to server
        # if server returns true, redirect to profile page
        # else, show error message
        username = request.form['username']
        password = request.form['password'] 

        data = {}
        data['username'] = username
        data['password'] = str(password)

        message = "u"
        message += json.dumps(data)
        message = message.encode('utf-8')
        client.send(message)

        from_server = client.recv(4096)
        from_server = from_server.decode('utf-8')
        print("From server : ",from_server)

        if from_server == "ERROR":
            flash('Kullanıcı adı veya şifre hatalı.', category='error')
            return render_template("signin.html")

        user_data = pd.read_json(from_server)
        user_data['userid'] = user_data['userid'].astype(str)

        user = User(user_data['userid'][0], user_data['personname'][0], user_data['personsurname'][0], user_data['e_mail'][0], user_data['telephoneno'][0], user_data['height'][0], user_data['weight'][0])
        
        login_user(user)

        # return render_template('test.html', test=user)
        

        return redirect(url_for('profile'))
          
    return render_template('signin.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    message = "g"
    message = message.encode('utf-8')
    client.send(message)
    
    from_server = client.recv(4096)
    from_server = from_server.decode('utf-8')
    print("From server : ",from_server)
    allAllergens = pd.read_json(from_server)
    return render_template('profile.html',allAllergens=allAllergens)

@app.route("/item/<int:barcodeno>")
def item(barcodeno):
    if not isDebug:
        global client
        if client is None:
            flash('Connection Error.', category='error')
            print("Cannot connect to server.")
            return render_template("index.html")
        barkod = barcodeno
        message = "b"
        message += str(barkod)
        message = message.encode('utf-8')
        client.send(message)
        
        from_server = client.recv(4096)
        from_server = from_server.decode('utf-8')
        print("From server : ",from_server)

        if from_server == "ERROR":
            flash('Barkod bulunamadı.', category='error')
            return render_template("index.html")

        # return render_template('test.html', test=from_server)
        data = pd.read_json(from_server)
        allergens = data["allergennames"][0].replace("'","\"")
        allergens = json.loads(allergens)
        return render_template('result.html', barcodeno=data['barcodeno'][0], foodname=data['foodname'][0], brand=data['brand'][0], weightvolume=data['weightvolume'][0], ingredients=data['ingredients'][0], fat=data['fat'][0], protein=data['protein'][0], carbs=data['carbs'][0], calorie=data['calorie'][0], allergens=allergens)
    else:
        from_server = "[{\"barcodeno\":1,\"foodname\":\"ekmek\",\"brand\":\"firinci\",\"weightvolume\":200,\"ingredients\":\"un\",\"fat\":20,\"protein\":10,\"carbs\":75,\"calorie\":300,\"allergennames\":\"['gluten', 'findik']\"}]"
        data = pd.read_json(from_server)
        allergens = data["allergennames"][0].replace("'","\"")
        allergens = json.loads(allergens)
        return render_template('result.html', barcodeno=data['barcodeno'][0], foodname=data['foodname'][0], brand=data['brand'][0], weightvolume=data['weightvolume'][0], ingredients=data['ingredients'][0], fat=data['fat'][0], protein=data['protein'][0], carbs=data['carbs'][0], calorie=data['calorie'][0], allergens=allergens)

@login_required
@app.route("/admin")
def admin():
    global client
    if client is None:
        flash('Connection Error.', category='error')
        print("Cannot connect to server.")
        return render_template("index.html")
    message = "g"
    message = message.encode('utf-8')
    client.send(message)
    
    from_server = client.recv(4096)
    from_server = from_server.decode('utf-8')
    print("From server : ",from_server)

    if from_server == "ERRORALLERGENS":
        flash('Alerjen bulunamadı.', category='error')
        return render_template("index.html")

    allAllergens = pd.read_json(from_server)
    return render_template('admin.html',allAllergens=allAllergens)

@login_required
@app.route("/admin/addproduct", methods=['GET', 'POST'])
def addproduct():
    if request.method == 'POST':
        global client
        if client is None:
            flash('Connection Error.', category='error')
            print("Cannot connect to server.")
            return render_template("index.html")

        message = "w"
        productname = request.form.get('productname')
        brand = request.form.get('brand')
        productbarcode = request.form.get('productbarcode')
        fat = request.form.get('fat')
        protein = request.form.get('protein')
        carbs = request.form.get('carbs')
        calorie = request.form.get('calorie')
        weightvolume = request.form.get('weightvolume')
        ingredients = request.form.get('ingredients')
        # get allergens
        req = "g"
        req = req.encode('utf-8')
        client.send(req)
        
        alg = client.recv(4096)
        alg = alg.decode('utf-8')
        print("From server : ",alg)

        if alg == "ERRORALLERGENS":
            flash('Alerjen bulunamadı.', category='error')
            return render_template("index.html")

        allAllergens = pd.read_json(alg) 
        print(allAllergens)
        allergens = []
        for i in range(len(allAllergens)):
            cur_allergen = allAllergens['allergenname'][i]
            if request.form.get(cur_allergen) is not None:
                allergens.append(cur_allergen)

        data = pd.DataFrame({'productname': [productname], 'brand': [brand], 'productbarcode': [productbarcode], 'fat': [fat], 'protein': [protein], 'carbs': [carbs], 'calorie': [calorie], 'weightvolume': [weightvolume], 'ingredients': [ingredients], 'allergenlist': [allergens]})
        data = data.to_json(orient='records')
        message += data
        message = message.encode('utf-8')
        client.send(message)

        from_server = client.recv(4096)
        from_server = from_server.decode('utf-8')
        print("From server : ",from_server)

        if from_server == "ERROR_ADD_ITEM":
            flash('Ürün eklenemedi.', category='error')
            return render_template("index.html")

        if from_server == "SUCCESS_ADD_ITEM":
            flash('Ürün başarıyla eklendi.', category='success')
            return render_template("index.html")
        
    return redirect('admin.html')

if __name__ == "__main__":
    app.run(debug=True,port=8080)