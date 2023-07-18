import pandas as pd
import numpy as np
import os
import math
os.chdir('C:.\Dados')

##Importando os dados para um data frame
df_mood = pd.read_csv('DASH - Moodle.csv',  sep=';', encoding = 'latin-1')
df_dac = pd.read_csv('DASH EAESPELHO.csv',  sep=';', encoding = 'latin-1')
##Vamos fazer a limpeza dos dados

ra_index_mood = df_mood[df_mood['MATRICULA RA'].str.isnumeric()==False].index #Aqui identificamos todas as linhas em que a matricula RA não é numérica no dataframe do moodle
ra_index_dac =  df_dac[df_dac['MATRICULA RA'].str.isnumeric()==False].index #Aqui identificamos todas as linhas em que a matricula RA não é numérica no dataframe da dac
#Precisamos identificar o que será feito com nestes casos

##Destes dataframes faremos outros menores, com os quais iremos trabalhar
##DF1 = número de disciplinas por unidade e instituição

df_merged = df_mood.merge(df_dac, how = 'outer', on = 'NOME CURTO')
df1_tot = df_merged.drop_duplicates(subset='NOME CURTO')
##Faremos a verificação de qual sistema hospeda as disciplinas

host = [None] * len(df1_tot) #criamos um array com none do comprimento do data frame 1. Este array irá armazenar as informações de hospedagem (Moodle, Dac)

#Usamos um for para identificar onde as disciplinas estão hospedadas
for x in range(0, len(df1_tot)):
    if isinstance(df1_tot.iloc[x].INSTITUICAO_x, str):
        host[x] = 'M'
    if isinstance(df1_tot.iloc[x].INSTITUICAO_y, str):
        host[x] = 'D'
    if isinstance(df1_tot.iloc[x].INSTITUICAO_x,str) and isinstance(df1_tot.iloc[x].INSTITUICAO_y,str):
        host[x] = 'MD'

#adicionamos a lista que acabamos de criar como uma coluna no df1_tot
df1_tot['host'] = host

##Faremos o trimming do dataframe para usarmos apenas as informações relevantes e sem duplicatas
INSTITUICAO = [None] * len(df1_tot)
NIVEL = [None] * len(df1_tot)
UNIDADE = [None] * len(df1_tot)


for x in range(0, len(df1_tot)):
    if df1_tot.iloc[x].host == 'M':
        INSTITUICAO[x] = df1_tot.iloc[x].INSTITUICAO_x
        NIVEL[x] = df1_tot.iloc[x].NIVEL_x
        UNIDADE[x] = df1_tot.iloc[x].UNIDADE_x

    if df1_tot.iloc[x].host == 'D':
        INSTITUICAO[x] = df1_tot.iloc[x].INSTITUICAO_y
        NIVEL[x] = df1_tot.iloc[x].NIVEL_y
        UNIDADE[x] = df1_tot.iloc[x].UNIDADE_y

    if df1_tot.iloc[x].host == 'MD':
        INSTITUICAO[x] = df1_tot.iloc[x].INSTITUICAO_y
        NIVEL[x] = df1_tot.iloc[x].NIVEL_y
        UNIDADE[x] = df1_tot.iloc[x].UNIDADE_y

##

df1_clean = pd.DataFrame(np.column_stack([INSTITUICAO,NIVEL,UNIDADE,df1_tot['NOME CURTO'],df1_tot['host']]),
             columns = ['INSTITUICAO', 'NIVEL','UNIDADE','NOME CURTO', 'host'])

##DF2 = NÚMERO DE ESTUDANTES POR DISCIPLINA
#Primeiro criamos arrays vazios onde serão adicionadas as informações
matric_tot=[]
nome_tot = []
papel_tot = []
##For loop para identificação dos alunos matriculados em cada disciplina
for z in range(0, len(df1_clean)):
    df_temp = df_merged[df_merged['NOME CURTO'] == df1_clean['NOME CURTO'][z]] #armazenamos um dataframe temporário apenas com o subset de uma disciplina (NOME CURTO)
    matric_temp = np.concatenate([df_temp['MATRICULA RA_x'].unique(), df_temp['MATRICULA RA_y'].unique()]) #juntamos em um vetor os RAs dos alunos dos sistemas do Moodle e da DAC
    matric_temp = matric_temp.astype(str) #transformamos tudo em string para poder comparar os valores (já que existem nomes e número de RA)
    matric_unique = np.unique(matric_temp) #selecionamos os valores únicos e excluímos as duplicatas
    NOME_CURTO = [None] * len(matric_unique) #criamos o NOME_CURTO com o mesmo tamanho dos número de alunos matrículados na disciplina
    PAPEL = [None] * len(matric_unique)
    for y in range(0,len(matric_unique)): #agora faremos a identificação do papel e da disciplina associado ao RA
        for x in range(0,len(df_temp)):
            if matric_unique[y] == df_temp['MATRICULA RA_x'].iloc[x]: #caso esteja armazenado apenas no Moodle, faremos a leitura ali
                NOME_CURTO[y] = df_temp['NOME CURTO'].iloc[x]
                PAPEL[y] = df_temp['PAPEL_x'].iloc[x]
            if matric_unique[y] == df_temp['MATRICULA RA_y'].iloc[x]: #caso esteja armazenado apenas na DAC, faremos a leitura ali
                NOME_CURTO[y] = df_temp['NOME CURTO'].iloc[x]
                PAPEL[y] = df_temp['PAPEL_y'].iloc[x]
    matric_tot = np.concatenate([matric_tot,matric_unique]) #concatenamos os resultados no nosso array
    nome_tot = np.concatenate([nome_tot, NOME_CURTO])
    papel_tot = np.concatenate([papel_tot, PAPEL])
##
df_aluno = pd.DataFrame(np.column_stack([matric_tot, nome_tot, papel_tot]), columns = ['MATRICULA RA','NOME CURTO','PAPEL'])

df2 =df_aluno.merge(df1_clean, how='left', on = 'NOME CURTO')

df2 = df2.dropna()

##
df2.to_csv('disciplinas.csv', header=False)

##
#Remover os arquivos com dados brutos
#os.remove('DASH - Moodle.csv')
#os.remove('DASH EAESPELHO.csv')