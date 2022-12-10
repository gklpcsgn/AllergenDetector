import pandas as pd
import pandasql as ps
import sqlalchemy as sal
from sqlalchemy import create_engine
import socket

# # connect to local host
# try:
#     engine = create_engine('postgresql://postgres:146146@localhost/Proje')
#     print('Connected to database.')
# except Exception as e:
#     print('Connection Error.')

# # select from allergen table
# allergen = pd.read_sql_query('select * from allergen',con=engine)

# print(allergen)


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(("", 1212))
print("listening")
serv.listen(5)
while True:
    conn, addr = serv.accept()
    from_client = ''
    while True:
        data_user = conn.recv(4096)
        if not data_user: break
        data_user = data_user.decode('utf-8')
        from_client += data_user
        print ("From client : ",from_client)
    conn.close()
    print ('client disconnected')

    # if ctrl+c is pressed end the loop
    if KeyboardInterrupt:
        break
    


# engine.dispose()



