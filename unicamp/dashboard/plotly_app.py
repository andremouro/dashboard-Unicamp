import dash
from dash import dcc, html
from .models import DACMOOD
from django_plotly_dash import DjangoDash
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

app = DjangoDash('SimpleExample')   # replaces dash.Dash
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
df2 = df.groupby(['unidade', 'nome_curto', 'papel']).count()['ra'].reset_index()

df2['papel'] = df2['papel'].replace({'P':'Docente', 'A':'Discente', 'F':'Formador'})

app.layout = html.Div([
    html.H1(children='Discentes e Docentes por Disciplinas', style={'textAlign': 'center'}),
    dcc.Dropdown(df2.unidade.unique(), 'INSTITUTO DE BIOLOGIA', id='dropdown-selection'),
    dcc.Graph(id='graph-content', style = {'height':600})
])


@app.callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df2[df2.unidade == value]
    return px.bar(dff, x='nome_curto', y='ra', color='papel', color_discrete_sequence=px.colors.qualitative.Antique,
                  labels={
                      'nome_curto': 'Sigla da Disciplina',
                      'ra': 'Quantidade',
                      'papel': 'Papel'
                  },
                  )


if 'SimpleExample' == '__main__':
    app.run_server(debug=True)