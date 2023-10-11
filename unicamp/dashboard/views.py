from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import File
from .models import DACMOOD
from .models import HOST
from .models import SOCIO
from .models import MESO
from django.views.generic import View
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import numpy as np
import os 
import time
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from datetime import date
from django.core import serializers

# Classe da nova view usando o banco de dados atualizados
class NewView(View):  # definimos a classe HomeView que será chamada dentro do urls.py
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index.html (que está dentro de irisjs)
        path = r'C:\Users\André\Desktop\DashboardUnicamp\Dados\espelho_comp.csv'
        ti_m = os.path.getmtime(path)
        
        m_ti = time.ctime(ti_m)
        m_ti = time.strptime(m_ti)
        m_ti = time.strftime("%d-%m-%Y %H:%M:%S", m_ti)
        
        data = DACMOOD.objects.all().values_list('ra','nome_curto','papel','instituicao','nivel','unidade')

        chart = [
            {
                'ra': data[i][0],
                'nome_curto': data[i][1],
                'papel': data[i][2],
                'instituicao': data[i][3],
                'nivel': data[i][4],
                'unidade': data[i][5],
            } for i in range(0,len(data))
        ]
        df = pd.DataFrame(chart)
        del chart, data
        
        
        # Dados para carga média das disciplinas por unidade
        carga = df.groupby(['unidade', 'papel']).count()['ra'].reset_index()

        # Tratamento dos dados. Remoção de duplicatas de usuários de cada uma das instituições e posterior combinação
        # em um único dataframe
        pessoas_U = df[df['instituicao'] == 'UNICAMP'].drop_duplicates('ra')
        pessoas_C = df[df['instituicao'] == 'COTUCA'].drop_duplicates('ra')
        pessoas_L = df[df['instituicao'] == 'COTIL'].drop_duplicates('ra')
        frames = [pessoas_U, pessoas_C, pessoas_L]
        pessoas = pd.concat(frames)
        del pessoas_U, pessoas_C, pessoas_L, frames

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
        del disc_U, disc_C, disc_L, frames
        
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
        
        df4_global = df3.groupby(['unidade']).count()['nome_curto'].reset_index()
        df4_global['tot'] = df3.groupby(['unidade']).sum()['ra'].reset_index()['ra']
        df4_global['mean'] = df4_global['tot'] / df4_global['nome_curto']
        df4_global.rename(columns={'mean': 'Média'}, inplace=True)
        
        
        # Dados para carga média das disciplinas por unidade
        carga = df.groupby(['unidade', 'instituicao', 'papel']).nunique()['ra'].reset_index()
        carga.rename(columns={'ra': 'Contagem'}, inplace=True)
        carga['papel'] = carga['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})
        
        carga_sum = df.groupby(['unidade']).nunique()['ra'].reset_index()
        carga_sum.rename(columns={'ra': 'Contagem'}, inplace=True)

        
        # Organização da estrutura de dados, como contagem do número de pessoas por instituição e por papel
        bar_df = pessoas.groupby(['instituicao', 'papel']).count()['ra'].reset_index()
        bar_df.rename(columns={'ra': 'Contagem'}, inplace=True)
        
        bar_df_sum = pessoas.groupby(['instituicao']).count()['ra'].reset_index()
        bar_df_sum.rename(columns={'ra': 'Contagem'}, inplace=True)
        
        # Organização da estrutura de dados, como contagem do número de pessoas por instituição e por papel
        bar_df_disc = disc.groupby(['instituicao', 'nivel']).count()['nome_curto'].reset_index()
        bar_df_disc.rename(columns={'nome_curto': 'Contagem'}, inplace=True)

        bar_df_disc_sum = disc.groupby(['instituicao']).count()['nome_curto'].reset_index()
        bar_df_disc_sum.rename(columns={'nome_curto': 'Contagem'}, inplace=True)

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
                     }, 
                     #color_discrete_map={'Docente': '#2A2F33', 'Discente': '#8C9493', 'Formador': '#8B8B94'},
                     color_discrete_sequence=px.colors.qualitative.Antique,
                     custom_data=["papel"],
                     hover_data={'instituicao':False})
                     
        bar.add_trace(go.Bar(name='Total', x = bar_df_sum['instituicao'], y = bar_df_sum['Contagem'], opacity = 0, showlegend=False))          

        bar.update_layout(hovermode='x unified', yaxis_range=[0,max(bar_df_sum['Contagem'])+1000], xaxis={'categoryorder': 'array',
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                   'Campus Campinas']})
                                                   
        bar.add_annotation(dict(y = max(bar_df_sum['Contagem'])+1000, x = 0.5, text = f"Total de pessoas: {sum(bar_df_sum['Contagem'])}", showarrow = False, bgcolor='white',
            font = dict(size = 18), borderpad = 10))

        del bar_df, bar_df_sum

        bar2 = px.bar(bar_df_disc, x="instituicao", y="Contagem", color="nivel",
                      title="Número disciplinas por instituição",
                      labels={
                          "instituicao": "Instituição",
                          "Contagem": "Número de disciplinas",
                          "nivel": "Nível"
                      },
                      color_discrete_map={'Ensino Médio': '#73909a', 'Graduação': '#ebd2b5',
                                          'Pós Graduação': '#99621f'},
                      hover_data={'instituicao':False})
                      
        bar2.add_trace(go.Bar(name = 'Total', x = bar_df_disc_sum['instituicao'], y = bar_df_disc_sum['Contagem'], opacity = 0, showlegend=False))    
                      
        bar2.update_layout(hovermode='x unified', yaxis_range=[0,max(bar_df_disc_sum['Contagem'])+1000],xaxis={'categoryorder': 'array',
                                  'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                    'Campus Campinas']})

        bar2.add_annotation(dict(y = max(bar_df_disc_sum['Contagem']+1000), x = 0.5, text = f"Total de disciplinas: {sum(bar_df_disc_sum['Contagem'])}", showarrow = False, bgcolor='white',
            font = dict(size = 18), borderpad = 10))
                                                    

        bar5 = px.bar(pie_df_disc, y='Contagem', x='unidade', title='Disciplinas por Unidade', color='unidade',
                      labels={
                          'Contagem': 'Número de disciplinas',
                          "unidade": 'Unidade'
                      },
                      color_discrete_sequence=px.colors.qualitative.Antique,
                      height=1000
                      )
                      
        bar5.add_annotation(dict(y = max(pie_df_disc['Contagem']+1000), x = 1, text = f"Total de disciplinas: {sum(bar_df_disc_sum['Contagem'])}", showarrow = False, bgcolor='white',
            font = dict(size = 18), borderpad = 10))
              
        del pie_df_disc


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
                      
        del bar_df_disc, bar_df_disc_sum              

        bar3 = px.bar(carga, x="unidade", y="Contagem", color="papel",
                      title="Matrículas por Unidade",
                      labels={
                          "unidade": "Unidade",
                          "Contagem": "Número de matrículas",
                          "papel": "Papel"
                      },
                      color_discrete_sequence=px.colors.qualitative.Antique,

                      height=1000,
                      hover_data={'unidade':False}
                      )

        bar3.add_annotation(dict(y = max(carga_sum['Contagem']+1000), x = 1, text = f"Total de matrículas: {sum(carga_sum['Contagem'])}", showarrow = False, bgcolor='white',
            font = dict(size = 18), borderpad = 10))
        bar3.update_layout(hovermode='x unified', yaxis_range=[0,max(carga_sum['Contagem'])+1000])
        bar3.add_trace(go.Bar(name = 'Total', x = carga_sum['unidade'], y = carga_sum['Contagem'], opacity = 0, showlegend=False))    

        del carga

        bar4 = px.bar(df4, x='unidade', y='Média', color='papel',
                      title='Média de matrículas por disciplina',
                      labels={
                          'unidade': 'Unidade',
                          'Média': 'Média de matrículas por disciplina',
                          'papel': 'Papel'
                      },
                      color_discrete_sequence=px.colors.qualitative.Antique,
                      height=1000)
                       
        del df4

        bar6 = px.bar(data_frame=df2, x='nome_curto', y='ra',
                      labels={
                          "nome_curto": "Disciplina",
                          "ra": "Número de matrículas",
                      }, height=1000,
                      title='Número de matrículas por disciplina'
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
        
        del df2
                
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
                'classe': x.CLASSE,
                'instituicao': x.instituicao,
                'nivel': x.nivel,
                'unidade': x.unidade,
                'sigla_uni': x.sigla_uni,
                'papel': x.papel,
                'idade': x.IDADE
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
            bar_sex_inst.add_trace(go.Bar(name = i, x = df_sex_inst1.loc[df_sex_inst1['sexo'] == i].instituicao, 
                        y = df_sex_inst1.loc[df_sex_inst1['sexo'] == i].ra,
                        marker_color = sex[i]))

        for j in nivel:
            for i in sex:
                bar_sex_inst.add_trace(go.Bar(name = i, x = df_sex_inst.loc[df_sex_inst['sexo'] == i].loc[ df_sex_inst['nivel'] == j].instituicao,
                            y = df_sex_inst.loc[df_sex_inst['sexo'] == i].loc[df_sex_inst['nivel'] == j].ra, 
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
            bar_sex_inst_pap.add_trace(go.Bar(name = i, x = df_sex_inst1.loc[df_sex_inst1['sexo'] == i].instituicao, 
                        y = df_sex_inst1.loc[df_sex_inst1['sexo'] == i].ra,
                        marker_color = sex[i]))

        for j in papel:
            for i in sex:
                bar_sex_inst_pap.add_trace(go.Bar(name = i, x = df_sex_inst_pap.loc[df_sex_inst_pap['sexo'] == i].loc[ df_sex_inst_pap['papel'] == j].instituicao,
                            y = df_sex_inst_pap.loc[df_sex_inst_pap['sexo'] == i].loc[df_sex_inst_pap['papel'] == j].ra, 
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
            bar_cor_inst.add_trace( go.Bar(name = i, x = df_cor_inst1.loc[df_cor_inst1['cor'] == i].instituicao, 
                        y = df_cor_inst1.loc[df_cor_inst1['cor'] == i].ra,
                        marker_color = colors[i]))
        
        for j in nivel:
            for i in colors:
                bar_cor_inst.add_trace(go.Bar(name = i, x = df_cor_inst.loc[df_cor_inst['cor'] == i].loc[ df_cor_inst['nivel'] == j].instituicao,
                            y = df_cor_inst.loc[df_cor_inst['cor'] == i].loc[df_cor_inst['nivel'] == j].ra,
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
            bar_cor_inst_papel.add_trace( go.Bar(name = i, x = df_cor_inst1.loc[df_cor_inst1['cor'] == i].instituicao, 
                        y = df_cor_inst1.loc[df_cor_inst1['cor'] == i].ra,
                        marker_color = colors[i]))
        
        for j in papel:
            for i in colors:
                bar_cor_inst_papel.add_trace(go.Bar(name = i, x = df_cor_inst.loc[df_cor_inst['cor'] == i].loc[ df_cor_inst['papel'] == j].instituicao,
                            y = df_cor_inst.loc[df_cor_inst['cor'] == i].loc[df_cor_inst['papel'] == j].ra,
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
                 'E':'#6F7A8B',
                 'D':'#BC996E',
                 'C':'#837D65',
                 'B':'#653D23',
                 'A':'#E7E3D9',                                                        
                 }
        
        
        bar_renda_inst = go.Figure()
         
        
            
        for i in rendas:
            bar_renda_inst.add_trace( go.Bar(name = i, x = df_renda_inst1.loc[df_renda_inst1['classe'] == i].instituicao, 
                    y = df_renda_inst1.loc[df_renda_inst1['classe'] == i].ra,
                    marker_color = rendas[i]))          

        for j in papel:
            for i in rendas:
                bar_renda_inst.add_trace(go.Bar(name = i, x = df_renda_inst.loc[df_renda_inst['classe'] == i].loc[ df_renda_inst['papel'] == j].instituicao,
                    y = df_renda_inst.loc[df_renda_inst['classe'] == i].loc[df_renda_inst['papel'] == j].ra,
                    marker_color = rendas[i], visible=False))
                                   

        bar_renda_inst.update_layout(updatemenus = [
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
            bar_renda_inst_papel.add_trace( go.Bar(name = i, x = df_renda_inst1.loc[df_renda_inst1['classe'] == i].instituicao, 
                    y = df_renda_inst1.loc[df_renda_inst1['classe'] == i].ra,
                    marker_color = rendas[i]))          

        for j in nivel:
            for i in rendas:
                bar_renda_inst_papel.add_trace(go.Bar(name = i, x = df_renda_inst.loc[df_renda_inst['classe'] == i].loc[df_renda_inst['nivel']==j].instituicao,
                    y = df_renda_inst.loc[df_renda_inst['classe'] == i].loc[df_renda_inst['nivel']==j].ra,
                    marker_color = rendas[i], visible=False))       

        bar_renda_inst_papel.update_layout(updatemenus = [
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
              
        bar_renda_inst_papel.update_layout(barmode = 'stack', title='Selecione o nível', xaxis=dict(title='Instituição'), 
                                       yaxis = dict(title='Número de pessoas'), hovermode='x unified')
            
        bar_renda_inst_papel.update_layout(xaxis={'categoryorder': 'array',
                                     'categoryarray': ['COTIL', 'COTUCA', 'Campus Piracicaba', 'Campi Limeira',
                                                       'Campus Campinas']})        
#########################################################################################        

        #Idade os estudantes por unidade e nível
        
        unidades = np.unique(df.unidade)
        
        df['papel'] = df['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})
        
        df_idade = df[['papel','unidade','nivel','idade']]
        
        nivel = {
            'ENSINO MÉDIO': '#ebd2b5', 
            'GRADUAÇÃO':'#99621f', 
            'PÓS GRADUAÇÃO':'#73909a'
        }

        papel = {
            'Docente' : px.colors.qualitative.Antique[0],
            'Discente': px.colors.qualitative.Antique[1],
            'Formador': px.colors.qualitative.Antique[2]
        
        }
        
        box_idade = go.Figure()
        
        for j in papel:
            box_idade.add_trace(go.Box(name = j, x = df_idade.loc[df['papel'] == j].unidade, y = df_idade.loc[df['papel'] == j].idade, marker_color = papel[j]))
        
        for j in papel:
            for i in nivel:
                box_idade.add_trace(go.Box(name = j, x = df_idade.loc[df['nivel'] == i].loc[df['papel']==j].unidade, y= df_idade[df_idade['nivel'] == i].loc[df_idade['papel'] == j].idade,
                          marker_color = papel[j], visible = False))
            
        box_idade.update_layout(xaxis=dict(title='Unidade'), 
                                       yaxis = dict(title='Média de idades'), showlegend = True)            

        box_idade.update_traces(hovertemplate = None, hoverinfo='skip')    
        
       
        
        box_idade.update_layout(updatemenus = [
                    dict(

                        buttons = list([
                            dict(label = 'Todos',
                                 method = 'update',
                                 args = [{'visible': [True]*3 +[False, False ,False]*3 }]),
                                 
                            dict(label = 'Ensino Médio',
                                 method = 'update',
                                 args=[{'visible': [False]*3 +[True, False ,False]*3}]
                        
                            ),
                            dict(label = 'Graduação',
                                 method = 'update',
                                 args=[{'visible': [False]*3 +[False, True ,False]*3}]
                        
                            ),
                            dict(label = 'Pós Graduação',
                                 method = 'update',
                                 args=[{'visible': [False]*3 +[False, False ,True]*3}]
                        
                            ),                            
                    ]), pad={"r": 10, "t": 10}, direction='down', x= 0.005, y=1.2, xanchor='left',yanchor='top')])  
                    
        box_idade.update_layout(boxmode = 'group', title='Selecione o nível', xaxis=dict(title='Unidade'), 
                                       yaxis = dict(title='Idade'), width = 1500, height = 500, yaxis_range=[0,80])

        box_idade.update_xaxes(tickangle=25)                                       
        

#########################################################################################        
        fig_sex_inst = plot(bar_sex_inst, output_type='div')
        fig_sex_inst_pap = plot(bar_sex_inst_pap, output_type='div')
        fig_cor_inst = plot(bar_cor_inst, output_type='div')
        fig_cor_inst_papel= plot(bar_cor_inst_papel, output_type='div')
        fig_renda_inst = plot(bar_renda_inst, output_type = 'div')
        fig_renda_inst_papel = plot(bar_renda_inst_papel, output_type = 'div')
        fig_idade = plot(box_idade, output_type = 'div')
        
        ctx = {'fig1': fig_sex_inst,'fig2': fig_sex_inst_pap, 'fig3': fig_cor_inst, 'fig4': fig_cor_inst_papel, 'fig6': fig_renda_inst, 'fig5': fig_renda_inst_papel, 'fig7':fig_idade}
        return render(request, 'dashboard/index3.html', ctx)
        
        

###################################################################
###################################################################      
#Criação da classe para visualização dos mapas e origem dos alunos. 
class MapView(View):
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index4.html 
        #Extração dos dados em formato geoJson
        with urlopen('https://raw.githubusercontent.com/giuliano-oliveira/geodata-br-states/main/geojson/br_states.json') as response:
            brasil = json.load(response)
        
        data = SOCIO.objects.all()
        chart = [
            {
                'ra': x.ra,
                'ESTADO': x.ESTADO,
                'MUNICIPIO': x.MUNICIPIO,
                'nivel': x.nivel,
                'papel': x.papel
            } for x in data
        ]
        #Armazenamos os dados dentro do dataframe 'df'
        df = pd.DataFrame(chart)        
        
        df['papel'] = df['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})
        df['nivel'] = df['nivel'].replace({'ENSINO MÉDIO': 'Ensino Médio', 'GRADUAÇÃO':'Graduação', 'PÓS GRADUAÇÃO': 'Pós Graduação'})
        df_est = df.loc[df['papel'] == 'Discente']
        df_est2 = df_est.groupby(['ESTADO']).count()['ra'].reset_index()
        df2 = df_est.groupby(['ESTADO','nivel']).count()['ra'].reset_index()
        
        
        sigla = ["NA"]* len(brasil['features'])
        codigo = ["NA"]* len(brasil['features'])

        for i in range(0,len(brasil['features'])):
            sigla[i] = brasil['features'][i]['properties']['SIGLA']
            codigo[i] = brasil['features'][i]['id']
            
        datas = pd.DataFrame({'Sigla':sigla,'id':codigo})


        df2['id'] = ['Na']*len(df2['ESTADO'])
        
        nivel = {
            'Ensino Médio' : px.colors.qualitative.Antique[0],
            'Graduação': px.colors.qualitative.Antique[1],
            'Pós Graduação': px.colors.qualitative.Antique[2]
        
        }

        for i in range(0, len(datas['Sigla'])):
            df2.loc[df2['ESTADO'] == datas['Sigla'][i], 'id'] = datas['id'][i]
            
        for i in range(0, len(datas['Sigla'])):
            df_est2.loc[df_est2['ESTADO'] == datas['Sigla'][i], 'id'] = datas['id'][i]            

        fig = go.Figure()
        
        fig.add_trace(go.Choropleth(
                locations = df_est2['id'], z = df_est2['ra'], colorscale='Blues', geojson = brasil,
                text = df_est2['ESTADO'],
                hovertemplate = 'Estado: %{text}<br>Quantidade:%{z}<extra></extra>', visible = True
            ))
        
        for i in nivel:
            fig.add_trace(go.Choropleth(
                locations = df2.loc[df2['nivel'] == i,'id'], z = df2.loc[df2['nivel'] == i,'ra'], colorscale='Blues', geojson = brasil,
                text = df2.loc[df2['nivel'] == i,'ESTADO'],
                hovertemplate = 'Estado: %{text}<br>Quantidade:%{z}<extra></extra>', visible = False
            ))

        
        fig.update_layout(updatemenus = [
                    dict(

                        buttons = list([
                        
                            dict(label = 'Todos',
                                 method = 'update',
                                 args = [{'visible': [True,False,False,False]}]
                            ),     
                            dict(label = 'Ensino Médio',
                                 method = 'update',
                                 args=[{'visible': [False,True,False,False]}]
                        
                            ),
                            dict(label = 'Graduação',
                                 method = 'update',
                                 args=[{'visible': [False,False,True,False]}]
                        
                            ),
                            dict(label = 'Pós Graduação',
                                 method = 'update',
                                 args=[{'visible': [False,False,False,True]}]
                        
                            )                            
                    ]), pad={"r": 10, "t": 10}, direction='down', x= 0.2, y=1.2, xanchor='left',yanchor='top')])  
                    
        fig.update_layout(boxmode = 'group', title='Selecione o nível', xaxis=dict(title='Unidade'), 
                                       yaxis = dict(title='Idade'), width = 1500, height = 500, yaxis_range=[0,80])

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        fig.update_geos(fitbounds = "locations", visible = False) 

##############################################################################
        
        data = MESO.objects.all()
        chart = [
            {
                'MESORRE': x.MESORRE,
                'MUNICIPIO': x.MUNICIPIO,
            } for x in data
        ]
        #Armazenamos os dados dentro do dataframe 'df'
        dfmeso = pd.DataFrame(chart)   
        dfmeso['MUNICIPIO'] = dfmeso['MUNICIPIO'].replace({r'\r': ''}, regex=True)


        with urlopen('https://raw.githubusercontent.com/fititnt/dados-referenciais-abertos/main/mesorregiao/geojson/mesorregiao.json') as response:
            meso = json.load(response)

        df2a = df_est.groupby(['MUNICIPIO']).count()['ra'].reset_index()
        df2a['MUNICIPIO'] = df2a['MUNICIPIO'].replace({r'\r': ''}, regex=True)

        df3 = df_est.groupby(['MUNICIPIO', 'nivel']).count()['ra'].reset_index()
        df3['MUNICIPIO'] = df3['MUNICIPIO'].replace({r'\r': ''}, regex=True)
 
                      
        for i in range(0, len(dfmeso['MUNICIPIO'])):
            dfmeso.loc[dfmeso['MUNICIPIO'] == dfmeso['MUNICIPIO'][i], 'MUNICIPIO'] = dfmeso['MUNICIPIO'][i].upper()



        for i in range(0, len(df2a['MUNICIPIO'])):
            df2a.loc[df2a['MUNICIPIO'] == df2a['MUNICIPIO'][i], 'MUNICIPIO'] = df2a['MUNICIPIO'][i].upper()

        for i in range(0, len(df2a['MUNICIPIO'])):
            dfmeso.loc[dfmeso['MUNICIPIO'] == df2a['MUNICIPIO'][i], 'Qtd'] = df2a['ra'][i]
        for i in range(0, len(dfmeso['MUNICIPIO'])):
            dfmeso.loc[dfmeso['MUNICIPIO'] == dfmeso['MUNICIPIO'][i], 'MESORRE'] = dfmeso['MESORRE'][i].upper()


        #Quantidade de alunos por mesorregiao por nivel
       
        MUNICIPIO = np.repeat(dfmeso['MUNICIPIO'],3)
        MESORRE = np.repeat(dfmeso['MESORRE'],3)
        nivel2 = ['Ensino Médio', 'Graduação','Pós Graduação']*645
        Qtd = ['Na']* len(MUNICIPIO)
        
        dfmeso2 = pd.DataFrame({'MUNICIPIO': MUNICIPIO,'MESORRE':MESORRE, 'nivel': nivel2, 'Qtd': Qtd})
        
        for i in range(0, len(df3['MUNICIPIO'])):
            df3.loc[df3['MUNICIPIO'] == df3['MUNICIPIO'][i], 'MUNICIPIO'] = df3['MUNICIPIO'][i].upper()        
          
        for i in range(0, len(df3['MUNICIPIO'])):
            dfmeso2.loc[(dfmeso2['MUNICIPIO'] == df3['MUNICIPIO'][i]) & (dfmeso2['nivel'] == df3['nivel'][i]), 'Qtd'] = df3['ra'][i]
        
       
        dfmeso = dfmeso.fillna(0)

        dfmeso.rename(columns = {'MESORRE': 'MESO'}, inplace = True)
        dfmeso = dfmeso.groupby(['MESO']).sum()['Qtd'].reset_index()

        dfmeso2.loc[(dfmeso2['Qtd'] == 'Na'), 'Qtd'] = 0
        
        dfmeso2.rename(columns = {'MESORRE': 'MESO'}, inplace = True)
        dfmeso2 = dfmeso2.groupby(['MESO','nivel']).sum()['Qtd'].reset_index()     
        
        fig2 = go.Figure()
          
        fig2.add_trace(go.Choropleth(
                        locations = dfmeso['MESO'], z = dfmeso['Qtd'], colorscale='Blues', geojson = meso,featureidkey = 'properties.MESO',
                        text = dfmeso['MESO'],
                        hovertemplate = 'Mesorregião: %{text}<br>Quantidade:%{z}<extra></extra>', visible = True
                    ))
                    
        for i in nivel:
            fig2.add_trace(go.Choropleth(
                locations = dfmeso2.loc[dfmeso2['nivel'] == i,'MESO'], z = dfmeso2.loc[dfmeso2['nivel'] == i,'Qtd'], colorscale='Blues', geojson = meso,featureidkey = 'properties.MESO',
                text = dfmeso2.loc[dfmeso2['nivel'] == i,'MESO'],
                hovertemplate = 'Mesorregião: %{text}<br>Quantidade:%{z}<extra></extra>', visible = False
            ))                   
                    
        fig2.update_layout(updatemenus = [
                    dict(

                        buttons = list([
                        
                            dict(label = 'Todos',
                                 method = 'update',
                                 args = [{'visible': [True,False,False,False]}]
                            ),     
                            dict(label = 'Ensino Médio',
                                 method = 'update',
                                 args=[{'visible': [False,True,False,False]}]
                        
                            ),
                            dict(label = 'Graduação',
                                 method = 'update',
                                 args=[{'visible': [False,False,True,False]}]
                        
                            ),
                            dict(label = 'Pós Graduação',
                                 method = 'update',
                                 args=[{'visible': [False,False,False,True]}]
                        
                            )                            
                    ]), pad={"r": 10, "t": 10}, direction='down', x= 0.3, y=1.2, xanchor='left',yanchor='top')])  
                    
        fig2.update_layout(boxmode = 'group', title='Selecione o nível', xaxis=dict(title='Unidade'), 
                                       yaxis = dict(title='Idade'), width = 800, height = 500, yaxis_range=[0,80])
        
                    

        fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        fig2.update_geos(fitbounds = "locations", visible = False)
        
        
###########################################################################################
        
        
        df2 = df2.loc[df2['ESTADO'] != 'SP']
        df3 = df2.groupby(['ESTADO']).sum()['ra'].reset_index().sort_values(by='ESTADO')
        
        df4 = df2.groupby(['ESTADO','nivel']).sum()['ra'].reset_index().sort_values(by='ESTADO')
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Pie(labels = df3['ESTADO'], values = df3['ra'], marker_colors = px.colors.qualitative.Pastel,
            hovertemplate = 'Estado: %{label}<br>Número de Discentes:%{value}<extra></extra>', sort = False))
            
        for i in nivel:
            fig3.add_trace(go.Pie(labels = df4.loc[df4['nivel'] == i, 'ESTADO'], values = df4.loc[df4['nivel'] == i, 'ra'], marker_colors = px.colors.qualitative.Pastel,
            hovertemplate = 'Estado: %{label}<br>Número de Discentes:%{value}<extra></extra>', sort = False))            
        
        fig3.update_layout(updatemenus = [
                    dict(

                        buttons = list([
                        
                            dict(label = 'Todos',
                                 method = 'update',
                                 args = [{'visible': [True,False,False,False]}]
                            ),     
                            dict(label = 'Ensino Médio',
                                 method = 'update',
                                 args=[{'visible': [False,True,False,False]}]
                        
                            ),
                            dict(label = 'Graduação',
                                 method = 'update',
                                 args=[{'visible': [False,False,True,False]}]
                        
                            ),
                            dict(label = 'Pós Graduação',
                                 method = 'update',
                                 args=[{'visible': [False,False,False,True]}]
                        
                            )                            
                    ]), pad={"r": 10, "t": 10}, direction='down', x= 0.8, y=1.2, xanchor='left',yanchor='top')])   

        fig3.update_layout(boxmode = 'group', title='Selecione o nível', xaxis=dict(title='Unidade'), 
                                       yaxis = dict(title='Idade'))
        
                    

        fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                    
        
        fig_brasil = plot(fig, output_type = 'div')
        fig_mun2 = plot(fig2, output_type = 'div')
        fig_pie = plot(fig3, output_type = 'div')
        ctx = {'fig1': fig_brasil, 'fig2': fig_mun2, 'fig3': fig_pie}
        return render(request, 'dashboard/index4.html', ctx)        
        
        
        
from django.db.models import Count     
from django.core.serializers.json import DjangoJSONEncoder      
from django.db.models import Case, When, Value, IntegerField


class TestView(View):  # definimos a classe HomeView que será chamada dentro do urls.py
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index.html (que está dentro de irisjs)
        path = r'C:\Users\André\Desktop\DashboardUnicamp\Dados\espelho_comp.csv'
        ti_m = os.path.getmtime(path)
        
        m_ti = time.ctime(ti_m)
        m_ti = time.strptime(m_ti)
        m_ti = time.strftime("%d-%m-%Y %H:%M:%S", m_ti)
        
       

        data = DACMOOD.objects.all().values_list('ra','nome_curto','papel','instituicao','nivel','unidade')

        chart = [
            {
                'ra': data[i][0],
                'nome_curto': data[i][1],
                'papel': data[i][2],
                'instituicao': data[i][3],
                'nivel': data[i][4],
                'unidade': data[i][5],
            } for i in range(0,len(data))
        ]
        df = pd.DataFrame(chart)
        del chart, data       
        
        #Contagem de matrículas por instituicao
        bar_df = df.groupby(['instituicao','papel']).nunique()['ra'].reset_index()
        bar_df.rename(columns={'ra': 'ra__count'}, inplace=True)   
        
        inst_order = ['COTIL','COTUCA','Campi Limeira','Campus Piracicaba','Campus Campinas']
        bar_df['CustomOrder'] = bar_df['instituicao'].apply(lambda x: inst_order.index(x))
        bar_df = bar_df.sort_values(by='CustomOrder')
        bar_df = bar_df.drop(columns=['CustomOrder'])
        
        json_str = bar_df.to_json(orient='records')
        ra_uniq = json.loads(json_str)

        #Contagem de disciplinas por instituicao
        disc_df = df.groupby(['instituicao','nivel']).nunique()['nome_curto'].reset_index()
        disc_df.rename(columns={'nome_curto': 'nome__count'}, inplace=True)   
        disc_df['CustomOrder'] = disc_df['instituicao'].apply(lambda x: inst_order.index(x))
        disc_df = disc_df.sort_values(by='CustomOrder')
        disc_df = disc_df.drop(columns=['CustomOrder'])
        
        json_str = disc_df.to_json(orient='records')
        disc_uniq = json.loads(json_str)        
        
        #Contagem de disciplinas por nivel
        disc_nivel_df = df.groupby(['nivel']).nunique()['nome_curto'].reset_index()
        disc_nivel_df.rename(columns={'nome_curto': 'nome__count'}, inplace=True)   
        labels = {'GRADUAÇÃO':'Graduação', 'PÓS GRADUAÇÃO':'Pós graduação', 'ENSINO MÉDIO': 'Ensino médio'}
        disc_nivel_df['nivel'] = disc_nivel_df['nivel'].map(labels)
        
        json_str = disc_nivel_df.to_json(orient='records')
        disc_nivel_df = json.loads(json_str)

        #Contagem de disciplinas por unidade
        disc_uni_df = df.groupby(['unidade']).nunique()['nome_curto'].reset_index()
        disc_uni_df.rename(columns={'nome_curto': 'nome__count'}, inplace=True)   
        
        json_str = disc_uni_df.to_json(orient='records')
        disc_uni_df = json.loads(json_str)        
        
        #Contagem de matrículas por unidade para cada nível
        mat_uni_df = df.groupby(['unidade','papel']).nunique()['ra'].reset_index()
        
        json_str = mat_uni_df.to_json(orient='records')
        mat_uni_df = json.loads(json_str)

        #Média de matrículas por disciplina em cada unidade
        mat_uni_sum = df.groupby(['unidade','nome_curto','papel']).nunique()['ra'].reset_index()
        mat_uni_tot = mat_uni_sum.groupby(['unidade','papel']).count()['nome_curto'].reset_index()
        mat_uni_tot['tot'] = mat_uni_sum.groupby(['unidade', 'papel']).sum()['ra'].reset_index()['ra']
        mat_uni_tot['mean'] = mat_uni_tot['tot']/mat_uni_tot['nome_curto']
        

        json_str = mat_uni_tot.to_json(orient='records')
        mat_uni_mean = json.loads(json_str)
        print(mat_uni_tot)
        
        #Fornecer os dados para o front-end
        ctx = {'ra_uniq': ra_uniq, 'disc_uniq': disc_uniq, 'disc_nivel_df': disc_nivel_df, 'disc_uni_df': disc_uni_df, 'mat_uni_df': mat_uni_df, 'mat_uni_mean': mat_uni_mean}
        
        return render(request, 'dashboard/index5.html', ctx)        
        
        
'''
        #Contagem dos RAs únicos em cada uma das instituições e ordenamento
        ra_uniq = DACMOOD.objects.all().values('instituicao', 'papel').annotate(Count('ra', distinct = True)).annotate(
            custom_order = Case(
                When(instituicao= 'COTIL', then=Value(1)),
                When(instituicao= 'COTUCA', then=Value(2)),
                When(instituicao= 'Campi Limeira', then=Value(3)),
                When(instituicao= 'Campus Piracicaba', then=Value(4)),
                When(instituicao= 'Campus Campinas', then=Value(5)),
                output_field=IntegerField(),
            )).order_by('custom_order')
      
        ra_uniq = json.dumps(list(ra_uniq))
        
        #Contagem de Disciplinas oferecidas em cada uma das instituições
        disc_inst = DACMOOD.objects.all().values('instituicao', 'nivel').annotate(Count('nome_curto', distinct=True)).annotate(
            custom_order = Case(
                When(instituicao= 'COTIL', then=Value(1)),
                When(instituicao= 'COTUCA', then=Value(2)),
                When(instituicao= 'Campi Limeira', then=Value(3)),
                When(instituicao= 'Campus Piracicaba', then=Value(4)),
                When(instituicao= 'Campus Campinas', then=Value(5)),
                output_field=IntegerField(),
            )).order_by('custom_order')
        disc_inst = json.dumps(list(disc_inst))
        print(disc_inst)
'''        