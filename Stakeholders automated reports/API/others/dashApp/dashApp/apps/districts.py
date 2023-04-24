import json
import io
import base64
import geopandas as gpd
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import utils.utils as utils
import utils.districts_figures as districts_figures

from app import app, engine

#--- upload shape file --
#shp_path = 'shapes/tl_2018_us_cd116/tl_2018_us_cd116.shp'
#gdf = gpd.read_file(shp_path)

#with open("shapes/districts") as geofile:
    #j_file = json.load(geofile)

with open("shapes/districts_simple.json") as geofile:
    j_file = json.load(geofile)

#------
layout = html.Div(className='main_container', children=[
    dbc.Row(
            dbc.Col(html.Div(className='title_container', children=[html.H5(id='district_name', children=[]), html.H6(id = 'year_txt', children=[])]))
        ),
    
    html.P(),
    
    dbc.Row(
        dbc.Col(dcc.Dropdown(id='dist_dropdown', 
            options=utils.get_districts(engine), 
            value='0101',
            style={"padding-left": "5px"}), width=2)
    ),

    dbc.Row([
        dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="share_dist", children=[]), html.P("Mexico's share of district exports")])])),
        dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="value_dist", children=[]), html.P("Value of district's exports to Mexico")])])),
        dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="jobs_dist", children=[]), html.P("District's total jobs")])])),
    ]),

    dbc.Row([
        dbc.Col(html.Div(className='table_container', children=[
            html.Center(html.H6(id='district_name_table', children=[])),
            html.Center(html.H6("Top exporting sectors to Mexico")),
            html.Div(id = 'dist_table', className='table', children=[]),
            html.P(className='footer', children=['Source: Estimated by The Trade Partnership (Washington, DC).'])
        ])),
        dbc.Col(html.Div(children=[
            html.P(), 
            html.Center(html.H5(id='state_map', children=[])), 
            html.Center(html.H6("Mexico's share of total district's exports")),
            dcc.Graph(id='map_dist', figure={})], className="image_container"))
    ]),

    dbc.Row(
            dbc.Col(html.Div(className='title_container', children=[html.H5(id ='product_name', children=[]), html.H6(id='year_prod')]))
        ),
    html.P(),

    dbc.Row(
        dbc.Col(dcc.Dropdown(id='prod_dropdown', options=utils.get_naics_labels(engine), value='00', style={"padding-left": "5px"}), width=4)
    ),

    dbc.Row([
        dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="share_prod", children=[]), html.P("Sector's share of total exports to Mexico")])])),
        dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="value_prod", children=[]), html.P("Value of sector's exports to Mexico")])])),
        dbc.Col(html.Div(className='mini_container', children=[html.Center([html.H5(id="jobs_prod", children=[]), html.P("Sector's total jobs")])])),
    ]),

    dbc.Row([
        dbc.Col(html.Div(className='table_container', children=[
            html.Center(html.H6(id='product_name_table', children=[])),
            html.Center(html.H6("Top exporting districts to Mexico")),
            html.Div(id = 'prod_table', className='table', children=[]),
            html.P(className='footer', children=['Source: Estimated by The Trade Partnership (Washington, DC).'])
        ])),
        dbc.Col(html.Div(children=[
            html.P(), 
            html.Center(html.H5(id='prod_map', children=[])), 
            html.Center(html.H6("District's share of total sector's exports")),
            dcc.Graph(id='map_all', figure={})], className="image_container"))
        #dbc.Col(html.Div(html.Iframe(id ='folium', width='100%', height='420')),className="image_container")
    ]),

])


@app.callback(
    [Output('dist_table', 'children'),
    #Output('map_dist', 'figure'),
    Output('district_name', 'children'),
    Output('share_dist', 'children'),
    Output('value_dist', 'children'),
    Output('jobs_dist', 'children'),
    #Output('state_map', 'children'),
    Output('year_txt', 'children'),
    Output('year_prod', 'children'),
    Output('district_name_table', 'children')],
    [Input('dist_dropdown', 'value')]
)
def update_dist(geoid):

    if geoid is None:
        geoid = '0101'

    dic = {'1':'st', '2':'nd', '3':'rd'}

    state = geoid[0:2]
    dist = geoid[2:4] if geoid[2] != '0' else geoid[3]

    #map_dist = districts_figures.map_dist(conn, geoid)
    df, state_name = districts_figures.get_dist_table(engine, geoid)
    dist_table = utils.df_to_table(df)

    district_name = '{} {}{} Congressional District'.format(state_name,dist, dic.get(dist[-1],'th'))

    share, value, jobs, year = districts_figures.get_district_boxes(engine, geoid)
    year_prod = 'Exports to Mexico by sector, {:.0f}'.format(year)
    year_txt = 'Exports to Mexico by Congressional District, {:.0f}'.format(year)

    return (dist_table, #map_dist, 
        district_name, 
        share, value, jobs, #state_name, 
        year_txt, year_prod, district_name)

@app.callback([
    Output('map_dist', 'figure'),
    Output('state_map', 'children')],
    [Input('dist_dropdown', 'value')]
)
def update_dist(geoid):
    if geoid is None:
        geoid = '0101'
    map_dist, state_name = districts_figures.map_dist(engine, geoid)

    return map_dist, state_name

@app.callback(
    [Output('prod_table', 'children'),
    #Output('map_all', 'figure'),
    Output('product_name', 'children'),
    Output('share_prod', 'children'),
    Output('value_prod', 'children'),
    Output('jobs_prod', 'children'),
    Output('product_name_table', 'children'),
    #Output('prod_map', 'children')
    ],
    [Input('prod_dropdown', 'value')]
)
def update_dist(code):

    if code is None:
        code = '00'

    #map_all = districts_figures.map_box(conn, j_file, code)
    df,  product_name = districts_figures.get_naics_df(engine, code)
    dist_table = utils.df_to_table(df) 
    share, value, jobs, = districts_figures.get_prod_boxes(engine, code)

    return (dist_table, #map_all,
     product_name, share, value, jobs, 
     product_name, #product_name
     )


@app.callback(
    [Output('map_all', 'figure'),
    Output('prod_map', 'children')],
    [Input('prod_dropdown', 'value')]
)
def update_map(code):

    if code is None:
        code = '00'
    
    map_all, prod_map = districts_figures.map_box(engine, j_file, code)

    return map_all, prod_map
