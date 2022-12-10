import pandas as pd
import pandasql as ps
import sqlalchemy as sal
from sqlalchemy import create_engine
import socket

# connect to local host
try:
    engine = create_engine('postgresql://postgres:146146@localhost/Proje')
    print('Connected to database.')
except Exception as e:
    print('Connection Error.')




serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(("", 1211))
print("listening")
serv.listen(5)
while True:
    conn, addr = serv.accept()

    while True:
        data_user = conn.recv(4096)
        if not data_user: break
        data_user = data_user.decode('utf-8')
        barcodeno = data_user
        print ("From client : ",barcodeno)

        # select from allergen table
        food = pd.read_sql_query('select * from food where barcodeno = ' + str(barcodeno),con=engine)
        allergen_id = pd.read_sql_query('select * from food_contains where barcodeno = ' + str(barcodeno),con=engine)['allergenid'].values
        allergen_names = []
        for i in allergen_id:
            allergen_names.append(pd.read_sql_query('select * from allergen where allergenid = ' + str(i),con=engine)['allergenname'].values[0])
        nutritions = pd.read_sql_query('select * from nutrition where barcodeno= ' + str(barcodeno),con=engine).drop(columns = ["barcodeno"])
        result = food.copy()
        result["allergenname"] = str(allergen_names)
        result["nutritions"] = nutritions.T[0].to_json()
        # convert to json
        test_data = result.to_json(orient='records')
        print(test_data)

        # send test_data to client
        test_data = test_data.encode('utf-8')
        conn.send(test_data)

    conn.close()
    print ('client disconnected')

    # if ctrl+c is pressed end the loop
    if KeyboardInterrupt:
        break
    


# engine.dispose()



