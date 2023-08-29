from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import File
from .models import DACMOOD
from .models import HOST
from .models import SOCIO
from django.views.generic import View
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import numpy as np
import os 
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Classe da nova view usando o banco de dados atualizados
class NewView(View):  # definimos a classe HomeView que será chamada dentro do urls.py
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index.html (que está dentro de irisjs)
        path = r'C:\Users\André\Desktop\DashboardUnicamp\Dados\espelho_comp.csv'
        ti_m = os.path.getmtime(path)
        
        m_ti = time.ctime(ti_m)
        m_ti = time.strptime(m_ti)
        m_ti = time.strftime("%d-%m-%Y %H:%M:%S", m_ti)
        
        data = DACMOOD.objects.all()
        chart = [
            {
                'ra': x.ra,
                'nome_curto': x.nome_curto,
                'papel': x.papel,
                'instituicao': x.instituicao,
                'nivel': x.nivel,
                'unidade': x.unidade,
            } for x in data
        ]
        df = pd.DataFrame(chart)

        # Dados para carga média das disciplinas por unidade
        carga = df.groupby(['unidade', 'papel']).count()['ra'].reset_index()

        # Tratamento dos dados. Remoção de duplicatas de usuários de cada uma das instituições e posterior combinação
        # em um único dataframe
        pessoas_U = df[df['instituicao'] == 'UNICAMP'].drop_duplicates('ra')
        pessoas_C = df[df['instituicao'] == 'COTUCA'].drop_duplicates('ra')
        pessoas_L = df[df['instituicao'] == 'COTIL'].drop_duplicates('ra')
        frames = [pessoas_U, pessoas_C, pessoas_L]
        pessoas = pd.concat(frames)
        pessoas.loc[pessoas['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS', ['instituicao']] = 'Campi Limeira'
        pessoas.loc[pessoas['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACIC', ['instituicao']] = 'Campus Piracicaba'
        pessoas.loc[
            pessoas['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campus Campinas'
        pessoas['papel'] = pessoas['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})

        # Tratamento dos dados; Número de disciplinas por instituição. Remoção de duplicatas de usuários de cada uma das instituições e posterior combinação em um único dataframe
        disc_U = df[df['instituicao'] == 'UNICAMP'].drop_duplicates('nome_curto')
        disc_C = df[df['instituicao'] == 'COTUCA'].drop_duplicates('nome_curto')
        disc_L = df[df['instituicao'] == 'COTIL'].drop_duplicates('nome_curto')
        frames = [disc_U, disc_C, disc_L]
        disc = pd.concat(frames)
        disc.loc[disc['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS', ['instituicao']] = 'Campi Limeira'
        disc.loc[disc['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACIC', ['instituicao']] = 'Campus Piracicaba'
        disc.loc[
            disc['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campus Campinas'

        disc['nivel'] = disc['nivel'].replace(
            {'ENSINO MÉDIO': 'Ensino Médio', 'GRADUAÇÃO': 'Graduação', 'PÓS GRADUAÇÃO': 'Pós Graduação'})

        # Tratamento para as cargas médias por disciplina de cada instituição
        df3 = df.groupby(['unidade', 'papel', 'nome_curto']).count()['ra'].reset_index()
        df4 = df3.groupby(['unidade', 'papel']).count()['nome_curto'].reset_index()
        df4['tot'] = df3.groupby(['unidade', 'papel']).sum()['ra'].reset_index()['ra']
        df4['mean'] = df4['tot'] / df4['nome_curto']
        df4.rename(columns={'mean': 'Média'}, inplace=True)
        df4['papel'] = df4['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})

        # Dados para carga média das disciplinas por unidade
        carga = df.groupby(['unidade', 'instituicao', 'papel']).nunique()['ra'].reset_index()
        carga.rename(columns={'ra': 'Contagem'}, inplace=True)
        carga['papel'] = carga['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})

        # Organização da estrutura de dados, como contagem do número de pessoas por instituição e por papel
        bar_df = pessoas.groupby(['instituicao', 'papel']).count()['ra'].reset_index()
        bar_df.rename(columns={'ra': 'Contagem'}, inplace=True)

        # Organização da estrutura de dados, como contagem do número de pessoas por instituição e por papel
        bar_df_disc = disc.groupby(['instituicao', 'nivel']).count()['nome_curto'].reset_index()
        bar_df_disc.rename(columns={'nome_curto': 'Contagem'}, inplace=True)

        # Dados para o gráfico de pizza
        pie_df_disc = disc.groupby(['unidade']).count()['nome_curto'].reset_index()
        pie_df_disc.rename(columns={'nome_curto': 'Contagem'}, inplace=True)

        #
        df2 = df.groupby(['unidade', 'nome_curto', 'papel']).count()['ra'].reset_index()

        # Gráfico de barras: Número de alunos e professores por instituição
        bar = px.bar(bar_df, x="instituicao", y="Contagem", color="papel",
                     title="Discente e docentes por instituição",
                     labels={
                         "instituicao": "Instituição",
                         "Contagem": "Número de discentes/docentes",
                         "papel": "Função"
                     }, color_discrete_map={'Docente': '#2A2F33', 'Discente': '#8C9493', 'Formador': '#8B8B94'},
                     custom_data=["papel"])

        bar.update_layout(xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})

        bar2 = px.bar(bar_df_disc, x="instituicao", y="Contagem", color="nivel",
                      title="Número disciplinas por instituição",
                      labels={
                          "instituicao": "Instituição",
                          "Contagem": "Número de disciplinas",
                          "nivel": "Nível"
                      },
                      color_discrete_map={'Ensino Médio': '#73909a', 'Graduação': '#ebd2b5',
                                          'Pós Graduação': '#99621f'}
                      )

        bar2.update_layout(xaxis={'categoryorder': 'array',
                                  'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                    'Campus Campinas']})

        bar5 = px.bar(pie_df_disc, y='Contagem', x='unidade', title='Disciplinas por Unidade', color='unidade',
                      labels={
                          'Contagem': 'Número de disciplinas',
                          "unidade": 'Unidade'
                      },
                      color_discrete_sequence=px.colors.qualitative.Antique,
                      height=1000
                      )

        pie2 = px.pie(bar_df_disc, values='Contagem', names='instituicao',
                      title='Disciplinas por Instituição',
                      labels={
                          'Contagem': 'Número de disciplinas',
                          "instituicao": 'Instituição'
                      },
                      color_discrete_sequence=('#B18642', '#AFBEA2', '#9CB4AC'),
                      category_orders={
                          'instituicao': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira', 'Campus Campinas']}
                      )

        pie3 = px.pie(bar_df_disc, values='Contagem', names='nivel', title='Disciplinas por nível',
                      labels={
                          'Contagem': 'Número de disciplinas',
                          "nivel": 'Nível'
                      },
                      color_discrete_sequence=('#ebd2b5', '#99621f', '#73909a')
                      )

        bar3 = px.bar(carga, x="unidade", y="Contagem", color="papel",
                      title="Discentes e docentes por Unidade",
                      labels={
                          "unidade": "Unidade",
                          "Contagem": "Número de discentes/docentes por Unidade",
                          "papel": "Papel"
                      },
                      color_discrete_sequence=px.colors.qualitative.Antique,

                      height=1000

                      )

        bar4 = px.bar(df4, x='unidade', y='Média', color='papel',
                      title='Média de discentes e docentes por disciplina',
                      labels={
                          'unidade': 'Unidade',
                          'Média': 'Média de discentes/docentes por disciplina',
                          'papel': 'Papel'
                      },
                      color_discrete_sequence=px.colors.qualitative.Antique,
                      height=1000)

        bar6 = px.bar(data_frame=df2, x='nome_curto', y='ra',
                      labels={
                          "nome_curto": "Disciplina",
                          "ra": "Número de discentes/docentes por Unidade",
                      }, height=1000,
                      title='Número de discentes/docentes por disciplina'
                      )

        bar6.add_shape(type="rect", xref='x domain', yref='y domain',
					   x0=0.92, y0=0.86, x1=0.998, y1=0.96,
					   line=dict(color='black'),
					   fillcolor='white'
					   )

        bar6.add_shape(type="rect", xref='x domain', yref='y domain',
                       x0=0.93, y0=0.93, x1=0.95, y1=0.95,
                       line=dict(color=px.colors.qualitative.Antique[2]),
                       fillcolor=px.colors.qualitative.Antique[2],
                       label=dict(text='Docente', textposition='middle left', padding=45)
                       )

        bar6.add_shape(type="rect", xref='x domain', yref='y domain',
                       x0=0.93, y0=0.90, x1=0.95, y1=0.92,
                       line=dict(color=px.colors.qualitative.Antique[1]),
                       fillcolor=px.colors.qualitative.Antique[1],
                       label=dict(text='Formador', textposition='middle left', padding=45)
                       )

        bar6.add_shape(type="rect", xref='x domain', yref='y domain',
					   x0=0.93, y0=0.87, x1=0.95, y1=0.89,
					   line=dict(color=px.colors.qualitative.Antique[0]),
					   fillcolor=px.colors.qualitative.Antique[0],
					   label=dict(text='Discente', textposition='middle left', padding=45)
					   )

        data_type = df2.unidade.unique()
        buttons = []

        for counter, i in enumerate(data_type):
            buttons.append(dict(method='update',
                                label='{}'.format(i),
                                args=[{
                                    'x': [df2[df2.unidade == i].nome_curto],
                                    'y': [df2[df2.unidade == i].ra],
                                    "marker": {"color": df2[df2.unidade == i].papel.map(
                                        {'P': px.colors.qualitative.Antique[2],
                                         'F': px.colors.qualitative.Antique[1],
                                         'A': px.colors.qualitative.Antique[0]})}
                                }]
                                ))

        bar6.update_layout(updatemenus=[dict(buttons=buttons,
                                             pad={"r": 10, "t": 10}, direction='down', x=0.5, y=1.15)])

        fig1 = plot(bar, output_type='div')
        fig2 = plot(bar2, output_type='div')
        fig3 = plot(bar5, output_type='div')
        fig4 = plot(pie2, output_type='div')
        fig5 = plot(pie3, output_type='div')
        fig6 = plot(bar3, output_type='div')
        fig7 = plot(bar4, output_type='div')
        fig8 = plot(bar6, output_type='div')
        ctx = {'fig1': fig1, 'fig2': fig2, 'fig3': fig3, 'fig4': fig4, 'fig5': fig5, 'fig6': fig6, 'fig7': fig7,
               'fig8': fig8, 'time' : m_ti}

        return render(request, 'dashboard/index.html', ctx)

class PopView(View):
    def get(self, request, *args,
            **kwargs):
        return render(request, 'dashboard/warning.html')

class HostView(View):
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index2.html 
        data = HOST.objects.all()
        chart = [
            {
                'nome_curto': x.nome_curto,
                'instituicao': x.instituicao,
                'nivel': x.nivel,
                'unidade': x.unidade,
                'sigla_uni': x.sigla_uni,
                'hosp': x.hosp,
            } for x in data
        ]
        df = pd.DataFrame(chart)
        df.loc[df['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS', ['instituicao']] = 'Campi Limeira'
        df.loc[df['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACIC', ['instituicao']] = 'Campus Piracicaba'
        df.loc[
            df['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campus Campinas'
        
        hosts = np.unique(df['hosp'])
        
        df['hosp'] = df['hosp'].replace([hosts[0], hosts[1], hosts[2], hosts[3]],['DAC', 'Classroom',  'Moodle', 'Moodle + Classroom'])
        
        #contagem de disciplinas por hospedagem em cada instituicao
        discp = df.groupby(['instituicao', 'hosp']).count()['nome_curto'].reset_index()
        
        #contagem de disciplinas por hospedagem em cada unidade
        discu = df.groupby(['unidade', 'hosp']).count()['nome_curto'].reset_index()
        
        bar = px.bar(discp, x="instituicao", y="nome_curto", color="hosp",
                    title="Número de disciplinas por local hospedado",
                     labels={
                         "instituicao": "Instituição",
                         "nome_curto": "Número de disciplinas",
                         "hosp": "Hospedagem"
                     }, color_discrete_map={'DAC': px.colors.qualitative.Antique[0], 'Classroom': px.colors.qualitative.Antique[1], 
                     'Moodle': px.colors.qualitative.Antique[2], 'Moodle + Classroom': px.colors.qualitative.Antique[3] })

        bar.update_layout(xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})
                                                   
                                                   
        pie2 = px.pie(discp, values='nome_curto', names='hosp',
                      title='Disciplinas por Hospedagem',
                      labels={
                          'nome_curto': 'Número de disciplinas',
                          "hosp": 'Hospedagem'
                      },
                      color_discrete_sequence=(px.colors.qualitative.Antique[0], px.colors.qualitative.Antique[1],px.colors.qualitative.Antique[2],
                      px.colors.qualitative.Antique[3]),
                      category_orders={
                          'instituicao': ['DAC', 'Classroom', 'Moodle', 'Moodle + Classroom']}
                      )

        bar2 = px.bar(discu, x='unidade', y='nome_curto', color = 'hosp',
                        title = 'Número de disciplinas por unidade',
                        labels={
                            'unidade': 'Unidade',
                            'nome_curto': 'Número de disciplinas',
                            'hosp': 'Hospedagem'
                        },
                        color_discrete_sequence=px.colors.qualitative.Antique,
                        height=1000)
                                                   
        fig1 = plot(bar, output_type='div')
        fig2 = plot(pie2, output_type='div')
        fig3 = plot(bar2, output_type='div')
        ctx = {'fig1': fig1, 'fig2':fig2, 'fig3':fig3}
        return render(request, 'dashboard/index2.html', ctx)
        

#Criação da classe para visualização dos dados socioeconomicos. Não será feita a modelagem dos dados com CR e CP.
class SocioView(View):
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index2.html 
        #Extração dos dados armazenados dentro do model SOCIO
        data = SOCIO.objects.all()
        chart = [
            {
                'ra': x.ra,
                'sexo': x.SEXO,
                'cor': x.COR_RACA,
                'fund1': x.ESC_FUNDAMENTAL1,
                'fund2': x.ESC_FUNDAMENTAL2,
                'medio': x.ESC_MEDIO,
                'est_civil': x.EST_CIVIL,
                'data_nasc': x.DATA_NASCIMENTO,
                'filhos': x.FILHOS,
                'classe': x.CLASSE,
                'nome_curto': x.nome_curto,
                'instituicao': x.instituicao,
                'nivel': x.nivel,
                'unidade': x.unidade,
                'sigla_uni': x.sigla_uni,
                'papel': x.papel
            } for x in data
        ]
        #Armazenamos os dados dentro do dataframe 'df'
        df = pd.DataFrame(chart)
        
        #Ajustar a nomenclatura de cada gênero, cor
        df['sexo'] = df['sexo'].replace(['F','M'],['Feminino', 'Masculino'])        
        df['cor'] = df['cor'].replace(['BRANCA','AMARELA','INDÍGENA','NÃO DECLARADA','PARDA','PRETA'],['Branca', 'Amarela','Indígena','Não Declarada','Parda','Preta'])        
        
        #Algumas correções no 'df'
        df.loc[df['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS', ['instituicao']] = 'Campi Limeira'
        df.loc[df['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACIC', ['instituicao']] = 'Campus Piracicaba'
        df.loc[
            df['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campus Campinas'

        #Primeiro, vamos um dataframe com a contagem de pessoas de cada sexo em cada instituição
        df_unique = df.drop_duplicates(subset=['ra'])
        df_sex_inst1 = df_unique.groupby(['instituicao', 'sexo']).count()['ra'].reset_index()
        df_sex_inst = df_unique.groupby(['instituicao', 'sexo','nivel']).count()['ra'].reset_index()
        
        #Construir um gráfico de barras com o número de pessoas de cada sexo por instituição
        sex = {
              'Feminino' : '#be4d25',
              'Masculino' : '#2596be'
        
        }
        
        nivel = ['ENSINO MÉDIO', 'GRADUAÇÃO', 'PÓS GRADUAÇÃO']
        
        bar_sex_inst = go.Figure()
        
        for i in sex:
            bar_sex_inst.add_trace(go.Bar(name = i, x = df_sex_inst1[df_sex_inst1.sexo == i].instituicao, 
                        y = df_sex_inst1[df_sex_inst1.sexo == i].ra,
                        marker_color = sex[i]))

        for j in nivel:
            for i in sex:
                bar_sex_inst.add_trace(go.Bar(name = i, x = df_sex_inst[df_sex_inst.sexo == i][ df_sex_inst.nivel == j].instituicao,
                            y = df_sex_inst[df_sex_inst.sexo == i][df_sex_inst.nivel == j].ra, 
                            marker_color = sex[i], visible=False))
                            
        bar_sex_inst.update_layout(barmode = 'stack', title='Selecione os níveis', xaxis=dict(title='Instituição'), 
                                   yaxis = dict(title='Número de pessoas'), hovermode='x unified')
        
        bar_sex_inst.update_layout(xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})  
                

        bar_sex_inst.update_layout(updatemenus = [
                dict(

                    buttons = list([
                        dict(

                             label = 'Todos',
                             method = 'update',
                             args=[{'visible': [True]*2+[False]*6}]
                    
                        ),
                        dict(label = 'Ensino Médio',
                             method = 'update',
                             args=[{'visible': [False]*2 + [True]*2 + [False]*4}]
                    
                        ),
                        dict(label = 'Graduação',
                             method = 'update',
                             args=[{'visible': [False]*4 + [True]*2 + [False]*2}]
                    
                        ),
                        dict(label = 'Pós Graduação',
                             method = 'update',
                             args=[{'visible': [False]*6 + [True]*2 }]
                    
                        )
                ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])

######################################################################################################################

        #Dataframe Sexo X Instituicao X Papel
        #Dataframe com a contagem de pessoas de cada sexo em cada instituição por papel
        df_unique = df.drop_duplicates(subset=['ra'])
        df_sex_inst_pap = df_unique.groupby(['instituicao', 'sexo','papel']).count()['ra'].reset_index()        
        
        papel = ['A', 'P', 'F']
        
        bar_sex_inst_pap = go.Figure()
        
        for i in sex:
            bar_sex_inst_pap.add_trace(go.Bar(name = i, x = df_sex_inst1[df_sex_inst1.sexo == i].instituicao, 
                        y = df_sex_inst1[df_sex_inst1.sexo == i].ra,
                        marker_color = sex[i]))

        for j in papel:
            for i in sex:
                bar_sex_inst_pap.add_trace(go.Bar(name = i, x = df_sex_inst_pap[df_sex_inst_pap.sexo == i][ df_sex_inst_pap.papel == j].instituicao,
                            y = df_sex_inst_pap[df_sex_inst_pap.sexo == i][df_sex_inst_pap.papel == j].ra, 
                            marker_color = sex[i], visible=False))
                            
        bar_sex_inst_pap.update_layout(barmode = 'stack', title='Selecione o papel desempenhado', xaxis=dict(title='Instituição'), 
                                   yaxis = dict(title='Número de pessoas'), hovermode='x unified')
        
        bar_sex_inst_pap.update_layout(xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})  
        
        bar_sex_inst_pap.update_layout(updatemenus = [
                dict(

                    buttons = list([
                        dict(

                             label = 'Todos',
                             method = 'update',
                             args=[{'visible': [True]*2+[False]*6}]
                    
                        ),
                        dict(label = 'Discente',
                             method = 'update',
                             args=[{'visible': [False]*2 + [True]*2 + [False]*4}]
                    
                        ),
                        dict(label = 'Docente',
                             method = 'update',
                             args=[{'visible': [False]*4 + [True]*2 + [False]*2}]
                    
                        ),
                        dict(label = 'Formador',
                             method = 'update',
                             args=[{'visible': [False]*6 + [True]*2 }]
                    
                        )
                ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])        





######################################################################################################################                        
        #Dataframe Raça X Instituição X Nivel
        df_cor_inst = df_unique.groupby(['instituicao','cor','nivel']).count()['ra'].reset_index()
        df_cor_inst1 = df_unique.groupby(['instituicao','cor']).count()['ra'].reset_index()

        #Gráfico de barras Raça X Instituicao X Nivel
        
             
        colors = {
                 'Branca':'#b2bbc7',
                 'Amarela':'#AB8F5E',
                 'Indígena':'#BB9B89',
                 'Parda':'#7C5440',
                 'Preta':'#433D3D',
                 'Não Declarada':'#4D7CA8'}
        
                 
        
        papel = ['A','P','F']
        
        bar_cor_inst = go.Figure()              
                
        for i in colors:
            bar_cor_inst.add_trace( go.Bar(name = i, x = df_cor_inst1[df_cor_inst1.cor == i].instituicao, 
                        y = df_cor_inst1[df_cor_inst1.cor == i].ra,
                        marker_color = colors[i]))
        
        for j in nivel:
            for i in colors:
                bar_cor_inst.add_trace(go.Bar(name = i, x = df_cor_inst[df_cor_inst.cor == i][ df_cor_inst.nivel == j].instituicao,
                            y = df_cor_inst[df_cor_inst.cor == i][df_cor_inst.nivel == j].ra,
                            marker_color = colors[i], visible=False))
        
                     
        bar_cor_inst.update_layout(barmode = 'stack', title='Selecione os níveis', xaxis=dict(title='Instituição'), 
                                   yaxis = dict(title='Número de pessoas'), hovermode='x unified')
        
        bar_cor_inst.update_layout(xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})  
                
        bar_cor_inst.update_layout(updatemenus = [
                dict(

                    buttons = list([
                        dict(

                             label = 'Todos',
                             method = 'update',
                             args=[{'visible': [True]*6+[False]*18}]
                    
                        ),
                        dict(label = 'Ensino Médio',
                             method = 'update',
                             args=[{'visible': [False]*6 + [True]*6 + [False]*12}]
                    
                        ),
                        dict(label = 'Graduação',
                             method = 'update',
                             args=[{'visible': [False]*12 + [True]*6 + [False]*6}]
                    
                        ),
                        dict(label = 'Pós Graduação',
                             method = 'update',
                             args=[{'visible': [False]*18 + [True]*6 }]
                    
                        )
                ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])

######################################################################################################################                        
        #Dataframe Raça X Instituição X Papel
        df_cor_inst = df_unique.groupby(['instituicao','cor','papel']).count()['ra'].reset_index()
        df_cor_inst1 = df_unique.groupby(['instituicao','cor']).count()['ra'].reset_index()

        #Gráfico de barras Raça X Instituicao X Papel
        
             
        colors = {
                 'Branca':'#b2bbc7',
                 'Amarela':'#AB8F5E',
                 'Indígena':'#BB9B89',
                 'Parda':'#7C5440',
                 'Preta':'#433D3D',
                 'Não Declarada':'#4D7CA8'}
        
                 
        
        papel = ['A','P','F']
        
        bar_cor_inst_papel = go.Figure()              
                
        for i in colors:
            bar_cor_inst_papel.add_trace( go.Bar(name = i, x = df_cor_inst1[df_cor_inst1.cor == i].instituicao, 
                        y = df_cor_inst1[df_cor_inst1.cor == i].ra,
                        marker_color = colors[i]))
        
        for j in papel:
            for i in colors:
                bar_cor_inst_papel.add_trace(go.Bar(name = i, x = df_cor_inst[df_cor_inst.cor == i][ df_cor_inst.papel == j].instituicao,
                            y = df_cor_inst[df_cor_inst.cor == i][df_cor_inst.papel == j].ra,
                            marker_color = colors[i], visible=False))
        
                     
        bar_cor_inst_papel.update_layout(barmode = 'stack', title='Selecione o papel desempenhado', xaxis=dict(title='Instituição'), 
                                   yaxis = dict(title='Número de pessoas'), hovermode='x unified')
        
        bar_cor_inst_papel.update_layout(xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})  
        
        
        bar_cor_inst_papel.update_layout(updatemenus = [
                dict(

                    buttons = list([
                        dict(

                             label = 'Todos',
                             method = 'update',
                             args=[{'visible': [True]*6+[False]*18}]
                    
                        ),
                        dict(label = 'Discente',
                             method = 'update',
                             args=[{'visible': [False]*6 + [True]*6 + [False]*12}]
                    
                        ),
                        dict(label = 'Docente',
                             method = 'update',
                             args=[{'visible': [False]*12 + [True]*6 + [False]*6}]
                    
                        ),
                        dict(label = 'Formador',
                             method = 'update',
                             args=[{'visible': [False]*18 + [True]*6 }]
                    
                        )
                ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])        
        
######################################################################################################################                        
        #Dataframe Renda X Instituição X Papel
        df_renda_inst = df_unique.groupby(['instituicao','classe','papel']).count()['ra'].reset_index()
        df_renda_inst1 = df_unique.groupby(['instituicao','classe']).count()['ra'].reset_index()

        #Gráfico de barras renda X Instituicao X Papel
        rendas = {
                 'E\r':'#6F7A8B',
                 'D\r':'#BC996E',
                 'C\r':'#837D65',
                 'B\r':'#653D23',
                 'A\r':'#E7E3D9',                                                        
                 }
        
        
        bar_renda_inst = go.Figure()
         
        
            
        for i in rendas:
            bar_renda_inst.add_trace( go.Bar(name = i, x = df_renda_inst1[df_renda_inst1.classe == i].instituicao, 
                    y = df_renda_inst1[df_renda_inst1.classe == i].ra,
                    marker_color = rendas[i]))          

        for j in papel:
            for i in rendas:
                bar_renda_inst.add_trace(go.Bar(name = i, x = df_renda_inst[df_renda_inst.classe == i][ df_renda_inst.papel == j].instituicao,
                    y = df_renda_inst[df_renda_inst.classe == i][df_renda_inst.papel == j].ra,
                    marker_color = rendas[i], visible=False))
                                   

        bar_renda_inst.update_layout(updatemenus = [
                    dict(

                        buttons = list([
                            dict(

                                 label = 'Todos',
                                 method = 'update',
                                 args=[{'visible': [True]*5+[False]*15}]
                        
                            ),
                            dict(label = 'Ensino Médio',
                                 method = 'update',
                                 args=[{'visible': [False]*5 + [True]*5 + [False]*10}]
                        
                            ),
                            dict(label = 'Graduação',
                                 method = 'update',
                                 args=[{'visible': [False]*10 + [True]*5 + [False]*5}]
                        
                            ),
                            dict(label = 'Pós Graduação',
                                 method = 'update',
                                 args=[{'visible': [False]*15 + [True]*5 }]
                        
                            )
                    ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])         
              
        bar_renda_inst.update_layout(barmode = 'stack', title='Selecione o papel', xaxis=dict(title='Instituição'), 
                                       yaxis = dict(title='Número de pessoas'), hovermode='x unified')
            
        bar_renda_inst.update_layout(xaxis={'categoryorder': 'array',
                                     'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                       'Campus Campinas']})    
 
#########################################################################################
        df_renda_inst = df_unique.groupby(['instituicao','classe','nivel']).count()['ra'].reset_index()
        df_renda_inst1 = df_unique.groupby(['instituicao','classe']).count()['ra'].reset_index()
        bar_renda_inst_papel = go.Figure()
         
        
            
        for i in rendas:
            bar_renda_inst_papel.add_trace( go.Bar(name = i, x = df_renda_inst1[df_renda_inst1.classe == i].instituicao, 
                    y = df_renda_inst1[df_renda_inst1.classe == i].ra,
                    marker_color = rendas[i]))          

        for j in nivel:
            for i in rendas:
                bar_renda_inst_papel.add_trace(go.Bar(name = i, x = df_renda_inst[df_renda_inst.classe == i][df_renda_inst.nivel==j].instituicao,
                    y = df_renda_inst[df_renda_inst.classe == i][df_renda_inst.nivel==j].ra,
                    marker_color = rendas[i], visible=False))       

        bar_renda_inst_papel.update_layout(updatemenus = [
                    dict(

                        buttons = list([
                            dict(

                                 label = 'Todos',
                                 method = 'update',
                                 args=[{'visible': [True]*5+[False]*15}]
                        
                            ),
                            dict(label = 'Discente',
                                 method = 'update',
                                 args=[{'visible': [False]*5 + [True]*5 + [False]*10}]
                        
                            ),
                            dict(label = 'Docente',
                                 method = 'update',
                                 args=[{'visible': [False]*10 + [True]*5 + [False]*5}]
                        
                            ),
                            dict(label = 'Formador',
                                 method = 'update',
                                 args=[{'visible': [False]*15 + [True]*5 }]
                        
                            )
                    ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])         
              
        bar_renda_inst_papel.update_layout(barmode = 'stack', title='Selecione o nível', xaxis=dict(title='Instituição'), 
                                       yaxis = dict(title='Número de pessoas'), hovermode='x unified')
            
        bar_renda_inst_papel.update_layout(xaxis={'categoryorder': 'array',
                                     'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                       'Campus Campinas']})        


 
#########################################################################################        
        fig_sex_inst = plot(bar_sex_inst, output_type='div')
        fig_sex_inst_pap = plot(bar_sex_inst_pap, output_type='div')
        fig_cor_inst = plot(bar_cor_inst, output_type='div')
        fig_cor_inst_papel= plot(bar_cor_inst_papel, output_type='div')
        fig_renda_inst = plot(bar_renda_inst, output_type = 'div')
        fig_renda_inst_papel = plot(bar_renda_inst_papel, output_type = 'div')
        
        ctx = {'fig1': fig_sex_inst,'fig2': fig_sex_inst_pap, 'fig3': fig_cor_inst, 'fig4': fig_cor_inst_papel, 'fig6': fig_renda_inst, 'fig5': fig_renda_inst_papel}
        return render(request, 'dashboard/index3.html', ctx)