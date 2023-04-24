import configparser
from sqlalchemy import create_engine
#import dash_core_components as dcc
from dash import dcc
from dash import html
#import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import macro, states, indicators, districts

app.layout = html.Div(children=[
    html.Div(children=html.H2("Commerce Statistics"), className='banner'), 
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Macro', value='tab-1'),
        dcc.Tab(label='Main indicators', value='tab-2'),
        #dcc.Tab(label='States', value='tab-3'),
        dcc.Tab(label='Districts', value='tab-4'),
    ]),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('tabs-example', 'value')])
def display_page(tab):
    if tab == 'tab-1':
        return macro.layout
    elif tab == 'tab-2':
        return indicators.layout
    elif tab == 'tab-3':
        return states.layout
    elif tab == 'tab-4':
        return districts.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)