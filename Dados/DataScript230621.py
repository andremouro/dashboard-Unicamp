import pandas as pd
import numpy as np
import os
import math
from datetime import date

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

#Corrigir dados
df_esp.loc[df_esp['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS', ['instituicao']] = 'Campi Limeira'
df_esp.loc[df_esp['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACICABA', ['instituicao']] = 'Campus Piracicaba'
df_esp.loc[df_esp['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campus Campinas'
df_esp['papel'] = df_esp['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'}) 


#aplicar hash aos RAs

#for i in range(0,len(df_esp['ra'])):
#    df_esp.loc[i, 'ra']=(hash(df_esp.loc[i, 'ra']))


#exportar o data frame normalizado como csv. Este é o primeiro df que será usado para quantificar 
#os alunos e professores por disciplina, etc.
df_esp.to_csv('espelho_comp.csv', encoding = 'latin-1', sep=';', index=False)

#Remover o arquivo com os dados brutos
#os.remove('DASH.eaespelho.todos.csv')

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

###############################################################################

#Importando os dados do arquivo Dash_Socioeconomico.csv
df_socio = pd.read_csv('DASH_Socioeconomico.csv',  sep=';', encoding = 'latin-1', dtype='unicode')
#Excluir linhas vazias
df_socio.dropna(inplace=True)

df_socio['CP'] = df_socio['CP'].str.replace(',','.').astype(float)
df_socio['CPE'] = df_socio['CPE'].str.replace(',','.').astype(float)
df_socio['CR'] = df_socio['CR'].str.replace(',','.').astype(float)
df_socio['CRP'] = df_socio['CRP'].str.replace(',','.').astype(float)

df_socio.rename(columns = {'MATRICULA_RA':'ra'}, inplace = True)

df_socio_comp = pd.merge(df_socio, df_esp, how = 'left', on = 'ra')

    
#Adicionar a coluna de classe social

df_socio_comp['CLASSE'] = 'NA'
df_socio_comp['RENDA_MES_FAMILIA'] = df_socio_comp['RENDA_MES_FAMILIA'].astype(int)

df_socio_comp.loc[df_socio_comp['RENDA_MES_FAMILIA'] < 2424.01, 'CLASSE'] = 'E'
df_socio_comp.loc[(df_socio_comp['RENDA_MES_FAMILIA'] > 2424 )&(df_socio_comp['RENDA_MES_FAMILIA'] < 4848.01 ), 'CLASSE'] = 'D'
df_socio_comp.loc[(df_socio_comp['RENDA_MES_FAMILIA'] > 4848 )&(df_socio_comp['RENDA_MES_FAMILIA'] < 12120.01 ), 'CLASSE'] = 'C'
df_socio_comp.loc[(df_socio_comp['RENDA_MES_FAMILIA'] > 12120 )&(df_socio_comp['RENDA_MES_FAMILIA'] < 22240.01 ), 'CLASSE'] = 'B'
df_socio_comp.loc[(df_socio_comp['RENDA_MES_FAMILIA'] > 22240 ), 'CLASSE'] = 'A'

#Adicionar a coluna de idade
IDADE = []
DATA_NASCIMENTO = pd.to_datetime(df_socio_comp['DATA_NASCIMENTO'], format = "%d/%m/%Y")

today = pd.to_datetime(date.today())

for i in range(0,len(DATA_NASCIMENTO)):
    IDADE.append(today.year - DATA_NASCIMENTO[i].year - ((today.month, today.day) < (DATA_NASCIMENTO[i].month, DATA_NASCIMENTO[i].day)))

df_socio_comp['IDADE'] = IDADE

temp_cols=df_socio_comp.columns.tolist()
index = df_socio_comp.columns.get_loc('ESTADO')
new_cols = temp_cols[0:index] + temp_cols[index+1:] + temp_cols[index:index+1]
df_socio_comp = df_socio_comp[new_cols]
temp_cols=df_socio_comp.columns.tolist()
index = df_socio_comp.columns.get_loc('MUNICIPIO')
new_cols = temp_cols[0:index] + temp_cols[index+1:] + temp_cols[index:index+1]
df_socio_comp = df_socio_comp[new_cols]

df_socio_comp.to_csv('dfsocioeco.csv', encoding = 'latin-1', sep=';', index=False)

