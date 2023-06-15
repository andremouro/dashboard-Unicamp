from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import File
from .models import DACMOOD
from django.views.generic import View
import pandas as pd
import plotly.express as px
from plotly.offline import plot


# Classe da nova view usando o banco de dados atualizados
class NewView(View):  # definimos a classe HomeView que será chamada dentro do urls.py
    def get(self, request, *args,
            **kwargs):  # esta classe fará que, quando requisitada (pela homepage da nossa aplicação web) seja renderizado o index.html (que está dentro de irisjs)
        data = DACMOOD.objects.all()
        chart = [
            {
                'ra': x.ra,
                'nome_curto': x.nome_curto,
                'papel': x.papel,
                'instituicao': x.instituicao,
                'nivel': x.nivel,
                'unidade': x.unidade,
                'hosp': x.hosp
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
        pessoas.loc[pessoas['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS  ', ['instituicao']] = 'Campi Limeira'
        pessoas.loc[pessoas['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACIC', ['instituicao']] = 'Campi Piracicaba'
        pessoas.loc[
            pessoas['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campi Campinas'
        pessoas['papel'] = pessoas['papel'].replace({'P': 'Docente', 'A': 'Discente', 'F': 'Formador'})

        # Tratamento dos dados; Número de disciplinas por instituição. Remoção de duplicatas de usuários de cada uma das instituições e posterior combinação em um único dataframe
        disc_U = df[df['instituicao'] == 'UNICAMP'].drop_duplicates('nome_curto')
        disc_C = df[df['instituicao'] == 'COTUCA'].drop_duplicates('nome_curto')
        disc_L = df[df['instituicao'] == 'COTIL'].drop_duplicates('nome_curto')
        frames = [disc_U, disc_C, disc_L]
        disc = pd.concat(frames)
        disc.loc[disc['unidade'] == 'FACULDADE DE CIÊNCIAS APLICADAS  ', ['instituicao']] = 'Campi Limeira'
        disc.loc[disc['unidade'] == 'FACULDADE DE ODONTOLOGIA DE PIRACIC', ['instituicao']] = 'Campi Piracicaba'
        disc.loc[
            disc['instituicao'] == 'UNICAMP', ['instituicao']] = 'Campi Campinas'

        disc['nivel'] = disc['nivel'].replace(
            {'ENSINO MEDIO': 'Ensino Médio', 'GRADUACAO': 'Graduação', 'POS GRADUACAO': 'Pós Graduação'})

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
                                 'categoryarray': ['COTIL', 'COTUCA', 'Campi Piracicaba', 'Campi Limeira',
                                                   'Campi Campinas']})

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
                                  'categoryarray': ['COTIL', 'COTUCA', 'Campi Piracicaba', 'Campi Limeira',
                                                    'Campi Campinas']})

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
                          'instituicao': ['COTIL', 'COTUCA', 'Campi Piracicaba', 'Campi Limeira', 'Campi Campinas']}
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
               'fig8': fig8}

        return render(request, 'dashboard/index.html', ctx)

class PopView(View):
    def get(self, request, *args,
            **kwargs):
        return render(request, 'dashboard/warning.html')
