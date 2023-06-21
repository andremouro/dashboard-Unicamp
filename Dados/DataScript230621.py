import pandas as pd
import numpy as np
import os
import math

#ler cada um dos bancos de dados
df_esp = pd.read_csv('DASH.eaespelho.todos.csv',  sep=';', encoding = 'latin-1', dtype='unicode')

#retiramos todos os espaços que podem aparecer ao final do nome da unidade
df_esp['UNIDADE'] = df_esp['UNIDADE'].str.replace("[ ]{2,}","",regex=True)

#adicionamos a matricula 00000 para alunos e professores não cadastrados corretamente
df_esp['MATRICULA RA'] = df_esp['MATRICULA RA'].str.replace("[ ]{2,}","00000",regex=True)

