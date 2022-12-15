import pandas as pd
import pandasql as ps
import sqlalchemy as sal
from sqlalchemy import create_engine
import socket
import json




    
# connect to local host
try:
    engine = create_engine('postgresql://postgres:146146@130.61.116.61/')
    print('Connected to database.')
except Exception as e:
    print('Connection Error.')
    exit()


def get_data_from_db_barcodeno(barcodeno):
    # select from allergen table
    food = pd.read_sql_query('select * from food where barcodeno = ' + '\'' + str(barcodeno) + '\'',con=engine)
    allergen_id = pd.read_sql_query('select * from food_contains where barcodeno = ' + '\'' + str(barcodeno) + '\'',con=engine)['allergenid'].values
    allergen_names = []

    for i in allergen_id:
        allergen_names.append(pd.read_sql_query('select * from allergen where allergenid = ' + str(i),con=engine)['allergenname'].values[0])

    nutritions = pd.read_sql_query('select * from nutrition where barcodeno= ' + '\'' + str(barcodeno) + '\'',con=engine).drop(columns = ["barcodeno"])
    result = pd.concat([food,nutritions], axis=1)
    result["allergennames"] = str(allergen_names)
    # convert to json
    test_data = result.to_json(orient='records')
    print(test_data)
    return test_data

def get_data_from_db_foodname(foodname):
    # select from allergen table
    query = 'select * from food where lower(foodname) like \'%%' + foodname + "%%\'"
    print(query)
    food = pd.read_sql_query(query ,con=engine)[["barcodeno","brand","foodname"]]
    food.head(10)
    test_data = food.to_json(orient='records')
    return test_data

def check_user_from_database(username,password):
    query = 'select * from person where e_mail = \'' + username + "\' and saltedpassword = \'" + password + "\'"
    print(query)
    user = pd.read_sql_query(query ,con=engine)
    user["userid"] = user["userid"].astype(str)
    test_data = user.to_json(orient='records')
    return test_data

def get_data_from_db_userid(userid):
    query = 'select * from person where userid = ' + str(userid)
    print(query)
    user = pd.read_sql_query(query ,con=engine)
    # set userid to string
    user["userid"] = user["userid"].astype(str)
    test_data = user.to_json(orient='records')
    return test_data

def get_allergens_from_db():
    query = 'select * from allergen'
    print(query)
    allergens = pd.read_sql_query(query,con=engine)
    test_data = allergens.to_json(orient='records')
    return test_data

def write_food_to_db(barcodeno,foodname,brand,weightvolume,ingredients):
    query = 'insert into food values (' + '\'' + str(barcodeno) + '\'' + ',\'' + foodname + '\',\'' + brand + '\',\'' + weightvolume + '\',\'' + ingredients + '\')'
    print(query)
    engine.execute(query)

def write_food_contains_to_db(barcodeno,allergennames):
    allergenid = []
    for allergen in allergennames:
        query = 'select * from allergen where allergenname = \'' + allergen + '\''
        print(query)
        allergenid.append(pd.read_sql_query(query,con=engine)['allergenid'].values[0])
    for i in allergenid:
        query = 'insert into food_contains values (' + '\'' + str(barcodeno) + '\'' + ',' + str(i) + ')'
        print(query)
        engine.execute(query)


def write_nutrition_to_db(fat,protein,carbs,calorie,barcodeno):
    query = 'insert into nutrition values (' + str(fat) + ',' + str(protein) + ',' + str(carbs) + ',' + str(calorie) + ',' + '\'' + str(barcodeno) + '\'' + ')'
    print(query)
    engine.execute(query)
    

def add_user_to_db(e_mail,personname,personsurname,telephoneno,saltedpassword,height,weight,is_admin):
    if telephoneno == '':
        telephoneno = 'NULL'
    else :
        telephoneno = '\'' + telephoneno + '\''
    if height == '':
        height = 'NULL'
    else:
        height = '\'' + height + '\''
    if weight == '':
        weight = 'NULL'
    else:
        weight = '\'' + weight + '\''
    query = 'insert into person(e_mail,personname,personsurname,telephoneno,saltedpassword,height,weight,is_admin) values (\'' + e_mail + '\',\'' + personname + '\',\'' + personsurname + '\',' + telephoneno + ',\'' + saltedpassword + '\',' + height + ',' + weight + ',' + str(is_admin) + ')'
    print(query)
    engine.execute(query)

def get_user_allergens_from_db(userid):
    query = 'select allergenname from allergen as a join personhasallergen as p on a.allergenid=p.allergenid where p.userid=' + str(userid) + ';'
    print(query)
    allergens = pd.read_sql_query(query,con=engine)
    test_data = allergens.to_json(orient='records')
    return test_data


def remove_food_from_db(barcodeno):
    # first remove from nutrition
    query = 'delete from nutrition where barcodeno = ' + '\'' + str(barcodeno) + '\''
    # then remove from food_contains
    query2 = 'delete from food_contains where barcodeno = ' + '\'' + str(barcodeno) + '\''
    # then remove from food
    query3 = 'delete from food where barcodeno = ' + '\'' + str(barcodeno) + '\''
    print(query)
    print(query2)
    print(query3)
    engine.execute(query)
    engine.execute(query2)
    engine.execute(query3)

def update_user_allergens(userid,allergennamesstring):
    # delete all user allergens
    import ast
    allergennames = ast.literal_eval(allergennamesstring)
    query = 'delete from personhasallergen where userid = ' + str(userid)
    print(query)
    engine.execute(query)
    # insert new allergens
    allergenid = []
    for allergen in allergennames:
        query = 'select * from allergen where allergenname = \'' + allergen + '\''
        print(query)
        allergenid.append(pd.read_sql_query(query,con=engine)['allergenid'].values[0])
    for i in allergenid:
        query = 'insert into personhasallergen values (' + str(i) + ',' + str(userid) + ')'
        print(query)
        engine.execute(query)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(("", 1214))
print("listening")
serv.listen(5)
while True:
    conn, addr = serv.accept()
    print("connected")
    while True:
        data_user = conn.recv(4096)
        print(data_user)
        if not data_user: break
        data_user = data_user.decode('utf-8')
        print ("From client : ",data_user)

        # GET FOOD BY BARCODE
        if data_user.startswith("b"):
            barcodeno = data_user[1:]
            try:
                test_data = get_data_from_db_barcodeno(barcodeno)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR"
        
        # CHECK USER FROM DATABASE
        elif data_user.startswith("u"):
            data = json.loads(data_user[1:])
            username = data["username"]
            password = data["password"]
            try:
                test_data = check_user_from_database(username,password)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_SEARCH_BY_BARCODE"

        # SIGN UP USER
        elif data_user.startswith("a"):
            userid = data_user[1:]
            try:
                test_data = get_data_from_db_userid(userid)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_AUTHENTICATION"
            
        # GET ALL ALLERGENS
        elif data_user.startswith("g"):
            try:
                test_data = get_allergens_from_db()
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_ALLERGENS"

        # WRITE FOOD TO DATABASE
        elif data_user.startswith("w"):
            # data is a food json
            data = json.loads(data_user[1:])
            print(data)
            productname = data[0]["productname"]
            brand = data[0]["brand"]
            productbarcode = data[0]["productbarcode"]
            fat = data[0]["fat"]
            protein = data[0]["protein"]
            carbs = data[0]["carbs"]
            calorie = data[0]["calorie"]
            weightvolume = data[0]["weightvolume"]
            ingredients = data[0]["ingredients"]
            allergenlist = data[0]["allergenlist"]

            try:
                write_food_to_db(productbarcode,productname,brand,weightvolume,ingredients)
                write_nutrition_to_db(fat,protein,carbs,calorie,productbarcode)
                write_food_contains_to_db(productbarcode,allergenlist)

                test_data = "SUCCESS_ADD_ITEM"
            except Exception as e:
                print('Cannot write data to database.')
                test_data = "ERROR_ADD_ITEM"

        # REMOVE FOOD FROM DATABASE
        elif data_user.startswith("r"):
            barcodeno = data_user[1:]
            try:
                remove_food_from_db(barcodeno)
                test_data = "SUCCESS_REMOVE_ITEM"
            except Exception as e:
                print('Cannot remove data from database.')
                test_data = "ERROR_REMOVE_ITEM"

        # GET USER ALLERGENS
        elif data_user.startswith("q"):
            userid = data_user[1:]
            try:
                test_data = get_user_allergens_from_db(userid)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_GET_USER_ALLERGENS"

        # UPDATE USER ALLERGENS
        elif data_user.startswith("p"):
            data = data_user[1:]
            userid = data[:1]
            allergenlist = data[1:]
            try:
                update_user_allergens(userid,allergenlist)
                test_data = "SUCCESS_UPDATE_USER_ALLERGENS"
            except Exception as e:
                print('Cannot update data from database.')
                print(e)
                test_data = "ERROR_UPDATE_USER_ALLERGENS"

        # ADD USER TO DATABASE
        elif data_user.startswith("s"):
            data = json.loads(data_user[1:])
            print(data)
            # insert into person(e_mail,personname,personsurname,telephoneno,saltedpassword,height,weight,is_admin) values('tak','Talha','Akbulut',null,'123456',145,40,False)
            e_mail = data[0]["e_mail"]
            personname = data[0]["personname"]
            personsurname = data[0]["personsurname"]
            telephoneno = data[0]["telephoneno"]
            saltedpassword = data[0]["saltedpassword"]
            height = data[0]["height"]
            weight = data[0]["weight"]
            try:
                add_user_to_db(e_mail,personname,personsurname,telephoneno,saltedpassword,height,weight,False)
                test_data = "SUCCESS_SIGNUP"
            except Exception as e:
                print('Cannot add user to database.')
                print(e)
                test_data = "ERROR_SIGNUP"
            

        # GET FOOD BY NAME
        else:
            foodname = data_user[1:]
            try:
                test_data = get_data_from_db_foodname(foodname)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_SEARCH_BY_NAME"

        test_data = test_data.encode('utf-8')
        conn.send(test_data)



    conn.close()
    print ('client disconnected')
    exit()

    # if ctrl+c is pressed end the loop
    


# engine.dispose()



