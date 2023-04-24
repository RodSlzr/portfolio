import configparser
from sqlalchemy import create_engine
import sys
from datetime import datetime, timedelta
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import utils.utils as utils
import utils.ind_figures as ind_figures

from app import app, conn, engine

cty_codes = pd.read_csv('data/ISO_codes1.csv')

layout = html.Div(className='main_container', children=[

       # dbc.Row([dbc.Col(html.Div([
        #dcc.Dropdown(
            #id='cat-dropdown',
            #options=[{'label':cat, 'value':num} for cat, num in catDict.items()],
            #value = ''
            #),
            #],style={'width': '100%', 'display': 'inline-block'})
            #)]),

        #dbc.Row([dbc.Col(html.Div([
        #dcc.Dropdown(
            #id='level2',
            #value = ''
            #),
            #],style={'width': '100%', 'display': 'inline-block'}
        #))]),

        #dbc.Row([dbc.Col(html.Div([
        #dcc.Dropdown(
            #id='level4',
            #value = ''
            #),
            #],style={'width': '100%', 'display': 'inline-block'}
        #))]),

        #dbc.Row([dbc.Col(html.Div([
        #dcc.Dropdown(
            #id='level6',
            #value = ''
            #),
            #],style={'width': '100%', 'display': 'inline-block'}
        #))]),

        #html.Hr(),
      
        #html.Div(id='display-selected-values'),

        #dbc.Row(dbc.Col(html.Div(children=[
            #dcc.Slider(
            #min=2,
            #max=6,
            #marks={i: 'H{}'.format(i) for i in [2,4,6]},
            #value=0,
            #)]))
        #),
        

        dbc.Row(dbc.Col(html.Div(children=[
            dcc.RadioItems(id="slct_type",
            options=[
                {"label": " Imports", "value": 'imp'},
                {"label": "  Exports", "value": 'exp'},
            ],
            value='exp',
            labelStyle={'display': 'inline-block', "padding": "12px", "margin": "auto"}
        )]), width=3)),

        dbc.Row(dbc.Col(html.Div(children=[
            dcc.RadioItems(id="slct_level",
            options=[
                {"label": " HS2", "value": 'H2'},
                {"label": "  HS4", "value": 'H4'},
                {"label": "  HS6", "value": 'H6'}
            ],
            value='H2',
            labelStyle={'display': 'inline-block', "padding": "12px", "margin": "auto"}
        )]), width=6)),

        dbc.Row([dbc.Col(html.Div([
        dcc.Dropdown(
            id='hs_dropdown',
            value = '-'
            ),
            ],style={'width': '100%', 'display': 'inline-block'}
        ))]),
        
        html.P(),
        
        dbc.Row(
            dbc.Col(html.Div(className='title_container', children=[html.H5(id='title1', children=[]), html.H6(id = 'title1_txt', children=[])]))
        ),

        #html.Hr(),
        #html.Div(id='display-selected-values'),

        dbc.Row([
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="val_month", children=[]), html.P(id="gdp_text", children=['Value Month (M)'])])])),
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="val_yr", children=[]), html.P(id="exp_text", children=['Value Year (M)'])])])),
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="m_growth", children=[]), html.P(id="imp_text", children=['Monthly growth (%)'])])])),
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="yr_growth", children=[]), html.P(id="eci_text", children=['Yearly growth (%)'])])])),
        ]),

        dbc.Row([
            dbc.Col(html.Div(children=[dcc.Graph(id='top10_m', figure={})], className="image_container")),
            dbc.Col(html.Div(children=[html.P(), html.Center(html.H5(id="map_title", children=[])), dcc.Graph(id='map', figure={})], className="image_container"))
        ]),

        dbc.Row([
            dbc.Col(html.Div(children=[dcc.Graph(id='top10_y', figure={})], className="image_container"))
        ]),

        #html.Hr(),
        dbc.Row(
            dbc.Col(html.Div(className='title_container', children=[html.H5(id='title2', children=['Time Series Analysis']), html.H6(id = 'title2_txt', children=[])]))
        ),
        
        html.P(),

        dbc.Row([dbc.Col(html.Div([
        dcc.Dropdown(
            id='cty_dropdown',
            value = '-'
            ),
            ],style={'width': '100%', 'display': 'inline-block'}
        ))]),

        dbc.Row([
            dbc.Col(html.Div(children=[dcc.Graph(id='decompose', figure={})], className="image_container")),
            #dbc.Col(html.Div(children=[dcc.Graph(id='exp_smth', figure={})], className="image_container"))
        ]),

        dbc.Row([
            dbc.Col(html.Div(children=[dcc.Graph(id='anomalies', figure={})], className="image_container")),
        ]),

    ])
'''
@app.callback(
    Output('level2', 'options'),
    [Input('cat-dropdown', 'value')]
)
def update_level2(parent):
    if parent != '':
        codes = utils.get_dropdown(conn, parent)
        rv = [{'label':name, 'value':code} for name, code in codes]
        rv = [{'label': 'Total, all commodities', 'value': ''}] + rv
    else:
        rv = [{'label': 'Total, all commodities', 'value': ''}]
    return rv

@app.callback(
    Output('level4', 'options'),
    [Input('level2', 'value')]
)
def update_level4(parent):
    if parent != '':
        codes = utils.get_dropdown(conn, parent)
        rv = [{'label':name, 'value':code} for name, code in codes]
        rv = [{'label': 'Total, all commodities', 'value': ''}] + rv
    else:
        rv = [{'label': 'Total, all commodities', 'value': ''}]
    return rv

@app.callback(
    Output('level6', 'options'),
    [Input('level4', 'value')]
)
def update_level6(parent):
    if parent != '':
        codes = utils.get_dropdown(conn, parent)
        rv = [{'label':name, 'value':code} for name, code in codes]
        rv = [{'label': 'Total, all commodities', 'value': ''}] + rv
    else:
        rv = [{'label': 'Total, all commodities', 'value': ''}]
    return rv
'''
@app.callback(
    [Output('title1', 'children'),
    Output('hs_dropdown', 'options')],
    [Input('slct_type', 'value'),
    Input('slct_level', 'value')]
)
def update_levels(com_type, hs):
    
    values = utils.get_dropdown_by_level(engine, com_type, hs)

    rv = [{'label':code + ' - ' + name, 'value':code} for name, code in values]
    rv = [{'label': 'Total, all commodities', 'value': '-'}] + rv
    
    var = 'Imports' if com_type == 'imp' else 'Exports'
    title1 = 'United States {} by Country'.format(var)
    
    return title1, rv


@app.callback(
    Output('cty_dropdown', 'options'),
    [Input('slct_type', 'value'),
    Input('hs_dropdown', 'value')])
    
def update_cty(com_type, comm_code):

    values = utils.get_cty_dropdown(engine, com_type, comm_code)

    rv = [{'label':code + ' - ' + name, 'value':code} for name, code in values]
    #rv = [{'label': 'Total, all commodities', 'value': '-'}] + rv
    
    return rv


@app.callback(
    [Output('title1_txt', 'children'),
    Output('map_title', 'children'),
    Output('map', 'figure')],
    
    [Input('slct_type', 'value'),
    Input('hs_dropdown', 'value')])

def set_display_children(com_type, hs):
    
    time = utils.get_max_date(engine)
    fig, comm = ind_figures.get_map(engine, com_type, hs, time, cty_codes)
    verb = 'Imports' if com_type == 'imp' else 'Exports'
    title = '{} of: {}'.format(verb, comm)

    return comm, title, fig


@app.callback(
    [Output('top10_m', 'figure'),
    Output('top10_y', 'figure'),
    Output('val_month', 'children'),
    Output('val_yr', 'children'),
    Output('m_growth', 'children'),
    Output('yr_growth', 'children'),
    ],
    
    [Input('slct_type', 'value'),
    Input('hs_dropdown', 'value')])

def set_display_children(com_type, hs):

    time = utils.get_max_date(engine)
    date_object = datetime.strptime(time, "%Y-%m")
    prev_month_time = str(date_object - timedelta(days=28)).split('-')[:2]
    prev_month_time = '-'.join(prev_month_time)
    prev_year_time = str(date_object - timedelta(days=365)).split('-')[:2]
    prev_year_time = '-'.join(prev_year_time)

    fig1, countries = ind_figures.get_top10_bar(engine, com_type, hs, time)
    fig2 = ind_figures.get_top10_lines(engine, com_type, hs, countries)
    val_month, val_yr = utils.val_month_year(engine, com_type, hs, time)
    prev_month, prev_month_acum = utils.val_month_year(engine, com_type, hs, prev_month_time)
    
    prev_year, prev_year_acum = utils.val_month_year(engine, com_type, hs, prev_year_time)
    month_growth = round((val_month - prev_month) / prev_month * 100, 2)
    year_growth = round((val_yr - prev_year_acum) / prev_year_acum * 100, 2)
    

    return fig1, fig2, val_month, val_yr, month_growth, year_growth


@app.callback(
    [Output('decompose', 'figure'),
     Output('anomalies', 'figure'),
     Output('title2_txt', 'children')],
    
    [Input('hs_dropdown', 'value'),
    Input('slct_type', 'value'),
    Input('cty_dropdown', 'value'),])


def set_display_children(hs, com_type, cty):

    data_series, com_name, country = ind_figures.data_series(engine, com_type, hs, cty)
    decompose_plot, trend, seasonal, resid = ind_figures.series_decompose(data_series, com_name, com_type, cty)
    anomalies = ind_figures.anomalies(data_series, trend, seasonal, resid, com_name, com_type, cty)
    
    return decompose_plot, anomalies, country


'''
@app.callback(
    [Output('cty_line', 'figure'),
    Output('moving_avg', 'figure'),
    Output('exp_smth', 'figure')
    ],
    
    [Input('hs_dropdown', 'value'),
    Input('slct_type', 'value'),
    Input('cty_dropdown', 'value'),])


def set_display_children(hs, com_type, cty):

    line_cty_fig = ind_figures.cty_line(engine, com_type, hs, cty)
    data_series, com_name = ind_figures.data_series(engine, com_type, hs, cty)
    moving_avg = ind_figures.moving_avg(data_series, com_name, 12, scale=1.96)
    exp_smth = ind_figures.plotExponentialSmoothing(data_series, com_name)

    return line_cty_fig, moving_avg, exp_smth
'''