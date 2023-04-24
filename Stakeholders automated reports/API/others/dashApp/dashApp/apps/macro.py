import configparser
from sqlalchemy import create_engine
import sys
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import utils.macro_figures as macro_figures
import utils.utils as utils

from app import app, engine

layout = html.Div(className='main_container', children=[    
        
        dbc.Row(dbc.Col(html.Div(children=[
            dcc.RadioItems(id="slct_country",
            options=[
                {"label": "  U.S.", "value": 'US'},
                {"label": "  Mexico", "value": 'MX'},
                {"label": "  Canada", "value": 'CA'}
            ],
            value='US',
            labelStyle={'display': 'inline-block', "padding": "12px", "margin": "auto"}
        )]), width=3)),
        
        dbc.Row([
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="gdp", children=[]), html.P(id="gdp_text", children=[])])])),
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="exp", children=[]), html.P(id="exp_text", children=[])])])),
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="imp", children=[]), html.P(id="imp_text", children=[])])])),
            dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="eci", children=[]), html.P(id="eci_text", children=[])])])),
        ]),

        dbc.Row(
            dbc.Col(html.Div(className='title_container', id='top', children=[html.H5(children=['Balance of Trade'])]))
        ),

        dbc.Row([
            dbc.Col(html.Div(className='table_container', children=[
                html.Center(html.H6(id='exp_country', children=[])), 
                html.Center(html.H6(children=['Total Goods Exports to Top Five Counterpart Economies,'])), 
                html.Center(html.H6(id='exp_year', children=[])), 
                html.Div(id = 'exp_table', className='table', children=[]),
                html.P(className='footer', children=['Source: UN Comtrade Database.'])
                ])),
            dbc.Col(html.Div(className='table_container', children=[
                html.Center(html.H6(id='imp_country', children=[])), 
                html.Center(html.H6(children=['Total Goods Imports from Top Five Counterpart Economies,'])), 
                html.Center(html.H6(id='imp_year', children=[])), 
                html.Div(id = 'imp_table', className='table', children=[]),
                html.P(className='footer', children=['Source: UN Comtrade Database.'])
                ])),
        ]),

        dbc.Row([
            dbc.Col(html.Div(children=[dcc.Graph(id='goods', figure={})], className="image_container")),
            dbc.Col(html.Div(children=[dcc.Graph(id='services', figure={})], className="image_container"))
        ]),

        dbc.Row(
            dbc.Col(html.Div(children=[dcc.Graph(id='com_timeline', figure={})], className="image_container"))
        ),

        dbc.Row(
            dbc.Col(html.Div(className='title_container', id='inv', children=[html.H5(children=['Foreign Investment'])]))
        ),

        dbc.Row([
            dbc.Col(html.Div(className='table_container', children=[
                html.Center(html.H6(id='inflow_country', children=[])), 
                html.Center(html.H6(children=['Inward Direct Investment from Top Five Counterpart Economies,'])), 
                html.Center(html.H6(id='inflow_year', children=[])), 
                html.Div(id = 'inflow_table', className='table', children=[]),
                html.P(className='footer', children=['Source: Coordinated Direct Investment Survey (CDIS), IMF.'])
                ])
            ),
            
            dbc.Col(html.Div(className='table_container', children=[
                html.Center(html.H6(id='outflow_country', children=[])), 
                html.Center(html.H6(children=['Outward Direct Investment in Top Five Counterpart Economies,'])), 
                html.Center(html.H6(id='outflow_year', children=[])), 
                html.Div(id = 'outflow_table', className='table', children=[]),
                html.P(className='footer', children=['Source: Coordinated Direct Investment Survey (CDIS), IMF.'])
                ])
            )
        ]),

        dbc.Row(
            dbc.Col(html.Div(children=[dcc.Graph(id='inv_imf', figure={})], className="image_container"))
        )

    ])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback([
    Output(component_id="gdp", component_property='children'),
    Output(component_id="gdp_text", component_property='children'),
    Output(component_id="exp", component_property='children'),
    Output(component_id="exp_text", component_property='children'),
    Output(component_id="imp", component_property='children'),
    Output(component_id="imp_text", component_property='children'),
    Output(component_id="eci", component_property='children'),
    Output(component_id="eci_text", component_property='children'),
    Output(component_id="exp_table", component_property='children'),
    Output(component_id="imp_table", component_property='children'),
    Output(component_id="exp_country", component_property='children'),
    Output(component_id="imp_country", component_property='children'),
    Output(component_id="exp_year", component_property='children'),
    Output(component_id="imp_year", component_property='children'),
    Output(component_id="goods", component_property='figure'),
    Output(component_id="services", component_property='figure'),
    Output(component_id="com_timeline", component_property='figure'),
    Output(component_id="inflow_table", component_property='children'),
    Output(component_id="outflow_table", component_property='children'),
    Output(component_id="inflow_country", component_property='children'),
    Output(component_id="outflow_country", component_property='children'),
    Output(component_id="inflow_year", component_property='children'),
    Output(component_id="outflow_year", component_property='children'),
    Output(component_id="inv_imf", component_property='figure'),
],
    [Input(component_id='slct_country', component_property='value')])

def update_country(country):

    dic = {'MX': 'Mexico', 'US': 'United States', 'CA': 'Canada'}
    
    #boxes
    gdp, gdp_yr = macro_figures.get_box_wb(engine, country, 'NY.GDP.PCAP.CD')
    imp, imp_yr = macro_figures.get_box_wb(engine, country, 'NE.IMP.GNFS.ZS')
    exp, exp_yr = macro_figures.get_box_wb(engine, country, 'NE.EXP.GNFS.ZS')
    eci, eci_yr = macro_figures.get_box_eci(engine, country)

    imp = '{}% of GDP'.format(imp)
    exp = '{}% of GDP'.format(exp)
    gdp_text = 'GDP per capita, {}'.format(gdp_yr)
    exp_text = 'Total Exports, {}'.format(exp_yr)
    imp_text = 'Total Imports, {}'.format(imp_yr)
    eci_text = 'ECI Rank, {}'.format(eci_yr)

    #balance of trade
    exp_df, exp_year = macro_figures.top_trade_df(engine, country, 'Export')
    exp_table = utils.df_to_table(exp_df)
    imp_df, imp_year = macro_figures.top_trade_df(engine, country, 'Import')
    imp_table = utils.df_to_table(imp_df)
    imp_country = dic[country]
    exp_country = dic[country]
    exp_year = '{}, US Dollars, Millions'.format(exp_year)
    imp_year = '{}, US Dollars, Millions'.format(imp_year)

    goods = macro_figures.balance_comtrade(engine, country, True)
    services = macro_figures.balance_comtrade(engine, country, False)
    com_timeline = macro_figures.trade_monthly(engine, country)
    
    # direct investment
    inflow_df, year_in = macro_figures.get_imf_df(engine, country, 'inward')
    inflow_table = utils.df_to_table(inflow_df)
    outflow_df, year_out = macro_figures.get_imf_df(engine, country, 'outward')
    outflow_table = utils.df_to_table(outflow_df)
    
    inflow_country = dic[country]
    outflow_country = dic[country]
    inflow_year = '{}, US Dollars, Millions'.format(year_in)
    outflow_year = '{}, US Dollars, Millions'.format(year_out)
    inv_imf = macro_figures.inv_imf(engine, country)

    return (gdp, gdp_text, exp, exp_text, imp, imp_text, eci, eci_text, 
        exp_table, imp_table, exp_country, imp_country, 
        exp_year, imp_year, goods, services, com_timeline, 
        inflow_table, outflow_table, inflow_country, outflow_country, inflow_year, 
        outflow_year, inv_imf)