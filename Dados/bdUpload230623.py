import mysql.connector
from mysql.connector import errorcode
import pandas as pd


#importando o csv com os dados
df_comp = pd.read_csv('espelho_comp.csv',  sep=';', encoding='latin-1')


cnx = mysql.connector.connect(user = 'root', password = '', host = 'localhost', database = 'mydb', allow_local_infile=True)

cursor = cnx.cursor()
sql = "DELETE FROM dashboard_dacmood"

cursor.execute(sql)

cnx.commit()

#for i in range(0, len(df_comp['id'])):
#    add_entry = ("INSERT INTO dashboard_dacmood (id, ra, nome_curto, papel, instituicao, nivel, unidade, sigla_uni) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
#    data_entry = (int(df_comp['id'][i]), str(df_comp['ra'][i]), str(df_comp['nome_curto'][i]), str(df_comp['papel'][i]), str(df_comp['instituicao'][i]), 
#    str(df_comp['nivel'][i]), str(df_comp['unidade'][i]), str(df_comp['sigla_uni'][i]))

#    cursor.execute(add_entry, data_entry)
    
#    cnx.commit()

cursor.execute("LOAD DATA LOCAL INFILE 'espelho_comp.csv' INTO TABLE dashboard_dacmood CHARACTER SET LATIN1 FIELDS TERMINATED BY ';' IGNORE 1 LINES")
cnx.commit()


cursor.close()
cnx.close()
