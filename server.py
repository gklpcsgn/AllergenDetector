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
    query = 'insert into food values (' + str(barcodeno) + ',\'' + foodname + '\',\'' + brand + '\',\'' + weightvolume + '\',\'' + ingredients + '\')'
    print(query)
    engine.execute(query)

def write_food_contains_to_db(barcodeno,allergenid):
    query = 'insert into food_contains values (' + str(barcodeno) + ',' + str(allergenid) + ')'
    print(query)
    engine.execute(query)

def write_nutrition_to_db(fat,protein,carbs,calorie,barcodeno):
    query = 'insert into nutrition values (' + str(fat) + ',' + str(protein) + ',' + str(carbs) + ',' + str(calorie) + ',' + str(barcodeno) + ')'
    print(query)
    engine.execute(query)
    
def write_user_to_db(e_mail,personname,telephoneno,saltedpassword,height,weight):
    query = 'insert into person(e_mail,personname,personsurname,telephoneno,saltedpassword,height,weight) values (\'' + e_mail + '\',\'' + personname + '\',\'' + telephoneno + '\',\'' + saltedpassword + '\',' + str(height) + ',' + str(weight) + ')'
    print(query)
    engine.execute(query)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(("", 1214))
print("listening")
serv.listen(5)
while True:
    conn, addr = serv.accept()

    while True:
        data_user = conn.recv(4096)
        print(data_user)
        if not data_user: break
        data_user = data_user.decode('utf-8')
        print ("From client : ",data_user)

        if data_user.startswith("b"):
            barcodeno = data_user[1:]
            try:
                test_data = get_data_from_db_barcodeno(barcodeno)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR"
        
        
        elif data_user.startswith("u"):
            # data is a username and password json
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

        elif data_user.startswith("a"):
            # data is a userid
            userid = data_user[1:]
            try:
                test_data = get_data_from_db_userid(userid)
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_AUTHENTICATION"
                
        elif data_user.startswith("g"):
            try:
                test_data = get_allergens_from_db()
                if test_data == "[]":
                    raise Exception
            except Exception as e:
                print('Cannot get data from database.')
                test_data = "ERROR_ALLERGENS"

        elif data_user.startswith("w"):
            # data is a food json
            data = json.loads(data_user[1:])
            productname = data["productname"]
            brand = data["brand"]
            productbarcode = data["productbarcode"]
            fat = data["fat"]
            protein = data["protein"]
            carbs = data["carbs"]
            calorie = data["calorie"]
            weightvolume = data["weightvolume"]
            ingredients = data["ingredients"]
            allergenlist = data["allergenlist"]

            try:
                write_food_to_db(productbarcode,productname,brand,weightvolume,ingredients)
                write_nutrition_to_db(fat,protein,carbs,calorie,productbarcode)
                write_food_contains_to_db(productbarcode,allergenlist)

                test_data = "OK"
            except Exception as e:
                print('Cannot write data to database.')
                test_data = "ERROR_ADD_ITEM"

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



