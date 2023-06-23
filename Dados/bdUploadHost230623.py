import mysql.connector
from mysql.connector import errorcode
import pandas as pd


#importando o csv com os dados
df_host = pd.read_csv('dftemp.csv',  sep=';', encoding='latin-1')


cnx = mysql.connector.connect(user = 'root', password = '', host = 'localhost', database = 'mydb')

cursor = cnx.cursor()


for i in range(0, len(df_host['id'])):
    add_entry = ("INSERT INTO dashboard_host (id, nome_curto, instituicao, nivel, unidade, sigla_uni, hosp) VALUES (%s, %s, %s, %s, %s, %s, %s)")
    data_entry = (int(df_host['id'][i]), str(df_host['nome_curto'][i]), str(df_host['instituicao'][i]), 
    str(df_host['nivel'][i]), str(df_host['unidade'][i]), str(df_host['sigla_uni'][i]), str(df_host['hosp'][i]))

    cursor.execute(add_entry, data_entry)

cnx.commit()

cursor.close()
cnx.close()