import mysql.connector
from mysql.connector import errorcode
import pandas as pd


#importando o csv com os dados

cnx = mysql.connector.connect(user = 'root', password = '', host = 'localhost', database = 'mydb')

cursor = cnx.cursor()

cursor = cnx.cursor()
sql = "DELETE FROM dashboard_host"

cursor.execute(sql)

cnx.commit()

cursor.execute("LOAD DATA LOCAL INFILE 'dftemp.csv' INTO TABLE dashboard_host CHARACTER SET LATIN1 FIELDS TERMINATED BY ';' IGNORE 1 LINES")
cnx.commit()

cnx.commit()

cursor.close()
cnx.close()