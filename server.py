import pandas as pd
import pandasql as ps
import sqlalchemy as sal
from sqlalchemy import create_engine

# connect to local host
engine = create_engine('postgresql://postgres:146146@localhost/Proje')

# select from allergen table
allergen = pd.read_sql_query('select * from allergen',con=engine)

print(allergen)

# close connection
engine.dispose()



