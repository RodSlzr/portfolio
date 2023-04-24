'''
Dash application
'''

from turtle import color
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import os.path as path
from plotly.subplots import make_subplots
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZ25vZ3VlZGEiLCJhIjoiY2wwa2Q4ZW1xMGZyaTNlbmVnMDJydHRvcCJ9.d17UBC8JGh_xhi29OHym0w'

def go_crime():
    #------------------------------------------------------------------------------
    # Application layout
    drr = path.abspath(path.join(__file__ ,"../.."))
    df = pd.read_csv(drr + "/data/fbi_twitter_merge/merged_data.csv")
    df = df.sort_values(['state', 'city', 'year', 'crimes_display'])
    title={'color':'black', 
        'font-weight': 'bold', 
        'font-family':'Arial', 
        'font-size': '250%',
        'text-align': 'center'}
        
    sentiment_values = ['Negative sentiment', 
                        'Negative sentiment (addictions)', 
                        'Negative sentiment (crimes)', 
                        'Negative sentiment (guns)', 
                        'Negative sentiment (hate)']

    app = Dash(
        __name__,
        external_stylesheets=[
            "https://codepen.io/chriddyp/pen/bWLwgP.css"
        ]
    )

    app.layout = html.Div([

        # Header
        html.Div(
            children=[
                html.H1("Crime and Twitter Analysis in the 10 major US cities, 2005-2019",
                        style=title),
                html.P('''This dashboard shows the prevalence of crime in the 10 major US cities 
                    from 2005 to 2019. It also shows the proportion of negative tweets within
                    each city for different sentiment analysis categories.''',
                    style={'font-size': '120%', 'font-family':'Arial'})]

        ),

        # Dropdowns
        html.Div([
            html.Div([
                dcc.Dropdown(id='crime_dropdown',
                    options=[{'label':str(b),'value':b} for b in sorted(df['type'].unique())],
                    placeholder="Select a type of crime/Twitter cluster",
                    multi=False,
                    value='All crimes')

                ], className="three columns"),

            html.Div([
                dcc.Dropdown(id='year_dropdown',
                    options=[{'label':str(b),'value':b} for b in sorted(df['year'].unique())],
                    placeholder="Select a year",
                    multi=False,
                    value=2019)

                ], className="two columns"),

            html.Div([
                dcc.Dropdown(id='crimes_unit',
                    options=[{'label':'Number of crimes','value':'number'}, 
                            {'label':'Crimes per 100,000 habitants','value':'100k'}],
                    placeholder="Select a crime unit",
                    multi=False,
                    value='100k')

                ], className="three columns"),

            html.Div([
                dcc.Dropdown(id='selected_cities',
                    options=[{'label':'10 major cities','value':'top10'}, 
                            {'label':'All cities','value':'all'}],
                    placeholder="Select cities",
                    multi=False,
                    value='top10')

                ], className="two columns"),

            html.Div([
                dcc.Dropdown(id='sentiment_type',
                    options=[{'label':str(b),'value':b} for b in sentiment_values],
                    placeholder="Select sentiment type",
                    multi=False,
                    value='Negative sentiment')

                ], className="two columns"),


        ], className="row"),

        # Graphs
        html.Div([
            html.Div([
                dcc.Graph(id="graph_output", 
                        figure={},
                        style={'height':'90vh'})
            ], className="eight columns"),
            html.Div([dcc.Graph(id="graph_types_output", 
                                figure={}, style={'height':'45vh', 'color': 'black'})], 
                    className="four columns"),
            html.Div([dcc.Graph(id="graph_time_output", 
                                figure={}, style={'height':'45vh'})], 
                    className="four columns"),



        ], className="row")

    ])


    #------------------------------------------------------------------------------
    # Display and update map according to selected year and type of crime

    @app.callback(
        Output("graph_output", "figure"),
        [Input("crime_dropdown", "value"),
        Input("year_dropdown", "value"),
        Input("crimes_unit", "value"),
        Input("selected_cities", "value")
        ]
    )

    def update_map(selected_crime, selected_year, crime_unit, selected_cities):

        print(f"Value user chose crime: {selected_crime}")
        print(f"Value user chose year: {selected_year}")
        print(f"Value user chose crime: {crime_unit}")
        print(f"Value user chose crime: {selected_cities}")

        df_map = df.copy()
        df_map = df_map.loc[df_map["type"].isin([selected_crime]) &
                            df_map["year"].isin([selected_year])
                            ]
        print(df_map)
        if crime_unit == 'number':
            df_map['crimes_display'] = df_map['number_crimes']
        if selected_cities == 'top10':
            df_map = df_map[df_map.large_city == 1]

        fig = px.scatter_mapbox(df_map,
                                lat = "lat",
                                lon = "lng",
                                color = df_map['crimes_display'],
                                labels={"crimes_display": "Number of crimes/<br>Twitter index"},
                                color_continuous_scale=px.colors.sequential.Sunsetdark,
                                size_max = 70,
                                zoom = 15,
                                hover_name = 'city',
                                size = 'population',
                                hover_data = ['year', 'city', 'state', 'population'],
                                title = "<b>Map of crimes/Twitter cluster</b><br><sup>Hover over a city<sup>"
                                )

        fig.update_layout(
            title_font_color = "#06184d",
            font_family='Arial',
            hovermode='closest',
            mapbox=dict(
                accesstoken=MAPBOX_ACCESS_TOKEN,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=39,
                    lon=-98
                ),
                pitch=0,
                zoom=3.2
            )
        )
        return fig


    #------------------------------------------------------------------------------
    # Display and update other figures according to selected year and type of crime

    @app.callback(
        Output("graph_types_output", "figure"),
        Output("graph_time_output", "figure"),
        [Input("graph_output", "hoverData"),
        Input("graph_output", "clickData"),
        Input("graph_output", "selectedData"),
        Input("crime_dropdown", "value"),
        Input("crimes_unit", "value"),
        Input("sentiment_type", "value")
        ]
    )

    def update_figure(hover_data, click_data, select_data, selected_crime, crime_unit, selected_sentiment):
        print(f'hover data: {hover_data}')

        hover_year = hover_data['points'][0]['customdata'][0]
        hover_city = hover_data['points'][0]['customdata'][1]
        hover_state = hover_data['points'][0]['customdata'][2]

        # Types of crime figure
        df_type_crime = df.copy()
        df_type_crime = df_type_crime[~df_type_crime['type'].isin(sentiment_values)]
        df_type_crime = df_type_crime.loc[df_type_crime["year"].isin([hover_year]) &
                            df_type_crime["city"].isin([hover_city]) &
                            df_type_crime["state"].isin([hover_state])                    
                            ]
        df_type_crime = df_type_crime.loc[df_type_crime["type"] != "All crimes"]
        if crime_unit == 'number':
            df_type_crime['crimes_display'] = df_type_crime['number_crimes']

        for c in df_type_crime.city.unique():
            display_c = c
            
        fig_crime_types = px.bar(df_type_crime,
                                x='crimes_display', 
                                y='type', 
                                orientation='h',
                                hover_name="year",
                                title= f'<b>Crime by type and year in {display_c}<b>')

        fig_crime_types.update_layout(
            title_font_color = "#06184d",
            yaxis_title=None,
            xaxis_title=None,
            font_family='Arial',
            margin=dict(l=120, b=1),
            template='none'
        )

        # Time series figure
        df_time = df.copy()
        df_time = df_time.loc[df_time["type"].isin([selected_crime, selected_sentiment]) &
                            df_time["city"].isin([hover_city]) &
                            df_time["state"].isin([hover_state])
                            ]
        if crime_unit == 'number':
            df_time['crimes_display'] = df_time['number_crimes']

        fig_time = make_subplots(specs=[[{"secondary_y": True}]])

        fig_time_crimes = px.line(df_time.loc[df_time["type"].isin([selected_crime])], 
                        x='year', 
                        y='crimes_display',
                        markers=True
                        )
        fig_time_crimes.update_traces(line_color='#46434d')

        fig_time_twitter = px.line(df_time.loc[df_time["type"].isin([selected_sentiment])], 
                        x='year', 
                        y='crimes_display',
                        markers=True
                        )
        fig_time_twitter.update_traces(yaxis="y2", line_color='#FC1CBF') 

        fig_time.add_traces(fig_time_crimes.data + fig_time_twitter.data)

    
        fig_time.update_layout(
            xaxis=dict(title=None),
            yaxis=dict(title="Crimes", titlefont=dict(color='#46434d')),
            yaxis2=dict(title="% Negative sentiment", titlefont=dict(color='#FC1CBF')),
            font_family='Arial',
            showlegend=False,
            template='none'
        )
        
        
        fig_crime_types.update_traces(marker_color='#46434d')
        
        return [fig_crime_types, fig_time]
    app.run_server(host = "127.0.0.1", port =8051, debug=False)
    #------------------------------------------------------------------------------
    #if __name__ == '__main__':
    #    app.run_server(debug=False)
