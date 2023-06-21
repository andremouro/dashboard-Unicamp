import pandas as pd
import numpy as np
import os
import math


#ler cada um dos bancos de dados
df_esp = pd.read_csv('DASH.eaespelho.todos.csv',  sep=';', encoding = 'latin-1', dtype='unicode')

#retiramos todos os espaços que podem aparecer ao final do nome da unidade
df_esp['UNIDADE'] = df_esp['UNIDADE'].str.replace("[ ]{2,}","",regex=True)

print(df_esp.head())

