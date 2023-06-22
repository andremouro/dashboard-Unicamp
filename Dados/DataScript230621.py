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

#ajustar os nomes das colunas de acordo com o models.py
df_esp = df_esp.rename(columns = {'INSTITUICAO': 'instituicao', 'NIVEL': 'nivel', 'UNIDADE':'unidade', 'UNIDADE SIGLA': 'sigla_uni', 'NOME CURTO': 'nome_curto', 'MATRICULA RA': 'ra', 'PAPEL':'papel'})

df_esp['id'] = range(0,len(df_esp['instituicao']))

df_esp = df_esp[['id','ra','nome_curto','papel','instituicao','nivel','unidade','sigla_uni']]

#exportar o data frame normalizado como csv. Este é o primeiro df que será usado para quantificar 
#os alunos e professores por disciplina, etc.
df_esp.to_csv('espelho_comp.csv', encoding = 'latin-1', sep=';', index=False)

###############################################################################

#criar um data frame apenas com a disciplina, inst e unidade, para identificar onde a disciplina
#está hospedada (moodle, classroom, os dois ou nenhum)

df_mood = pd.read_csv('DASH.Disciplinas.Moodle.csv',  sep=';', dtype='unicode')
df_class = pd.read_csv('DASH.Disciplinas.GClassroom.csv',  sep=';', dtype='unicode')

df_mood = df_mood.rename(columns = {'NOME CURTO': 'nome_curto'})
df_class = df_class.rename(columns = {'NOME CURTO': 'nome_curto'})

df_uniDisc = df_esp.drop_duplicates(subset=['nome_curto']).drop(['ra','papel'],axis=1)

df_comp = pd.merge(df_uniDisc, df_mood, how='left', on='nome_curto')
df_comp = pd.merge(df_comp, df_class, how = 'left', on='nome_curto')

#juntar as duas colunas com Moodle e GoogleClassroom em apenas uma
df_comp['hosp'] = (df_comp['ORIGEM_x'].fillna('')+'_'+df_comp['ORIGEM_y'].fillna('')).str.strip('_') 


#classificar disciplinas que não estão no moodle nem no classroom dentro da dac.
df_comp['hosp'] = df_comp['hosp'].str.replace(r'^\s*$', "DAC", regex=True)


df_comp = df_comp.drop(['ORIGEM_x','ORIGEM_y'],axis=1)

#exportar segunda tabela com local de hospedagem de cada disciplina
df_comp.to_csv('dftemp.csv', encoding = 'latin-1', sep=';', index=False)