import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app

layout = html.Div(children=[    
        dbc.Row(dbc.Col(html.Div(dcc.Dropdown(id="slct_country",
                 options=[
                     {"label": "U.S.", "value": 'US'},
                     {"label": "México", "value": 'Mexico'},
                     {"label": "Canadá", "value": 'Canada'}
                     ],
                 multi=False,
                 value='US',
                 style={'width': "40%"}, 
                 )))),
        
        dbc.Row(
            dbc.Col(html.Div(className='mini_container', children=[html.H6(id="output", children=[]), html.P("Selected")]))
        )
    ])

@app.callback(
    Output(component_id="output", component_property='children'),
    [Input(component_id='slct_country', component_property='value')])

def update_count(option_slctd):
    
    selected = option_slctd

    return selected