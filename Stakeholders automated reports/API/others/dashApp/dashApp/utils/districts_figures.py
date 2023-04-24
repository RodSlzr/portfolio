import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import json
import numpy as np


def map_box(engine, j_file, NAICS4):
    '''
    '''

    if NAICS4 != '00':
        query = '''SELECT description, CD, ST, GEOID, VALMX / 1000000 AS value, (VALMX * 100) / (SELECT sum(VALMX) FROM nafta_mexico 
                WHERE NAICS = :1) As "Share" FROM nafta_mexico 
            WHERE NAICS = :2
            '''
        df = pd.read_sql(query, engine, params=(NAICS4, NAICS4))
        prod_name = df.description.unique()[0]

    else:
        query = '''SELECT CD, ST, GEOID, sum(VALMX) / 1000000 AS value FROM nafta_mexico 
            GROUP BY CD, ST, GEOID
            '''    
        df = pd.read_sql(query, engine)
        prod_name = 'Total, all sectors'
        df['Share'] = df['value'] * 100 / df['value'].sum()

    df = df.rename(columns={"Share": "Share (%)", "st": "ST", "cd": "CD", "value": "Value (M)", "geoid": "GEOID"}) 


    fig = px.choropleth_mapbox(df, geojson=j_file, locations="GEOID", featureidkey="properties.GEOID",
                            color="Share (%)",
                            mapbox_style="carto-positron",
                            zoom=2.7, center = {"lat": 37.0902, "lon": -95.7129},
                            opacity=0.5,
                            hover_name='ST',
                            hover_data={'GEOID': False, 'CD': True, 'Share (%)': ':.1f', 'ST': False, 'Value (M)':':,.1f'},
                            )
    fig.update_layout(margin={"r":5,"t":0,"l":5,"b":5},
        font_color="black",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',)

    return fig, prod_name


def map_dist(engine, geoid):

    state = geoid[0:2]
    dist = geoid[2:4]

    with open("shapes/state_{}".format(state)) as geofile:
        j_file = json.load(geofile)
    
    query1 = '''
        SELECT GEOID, (sum(Value_mx) * 100 / sum(Value_world)) AS 'Share (%)', STATE_NAME, CD
        FROM nafta_mexico 
        WHERE STATE = ?
        GROUP BY GEOID
        '''
    
    query = '''SELECT GEOID, STNAME, CD , (sum(VALMX) / sum(VALWORLD) * 100) as sh
        FROM nafta_mexico
        WHERE state = :1
        GROUP BY CD, STNAME, GEOID'''
    
    
    df = pd.read_sql(query, engine, params=(state,))
    df = df.rename(columns={"sh": "Share (%)", "stname": "STNAME", "cd": "CD", "geoid": "GEOID"}) 
    state_name = df.STNAME.unique()[0]

    fig = px.choropleth(df, geojson=j_file, color="Share (%)",
                    locations="GEOID", featureidkey="properties.GEOID",
                    projection="mercator",
                    hover_name='CD',
                    hover_data={'GEOID': False,'Share (%)': ':.1f', 'STNAME': False, 'CD': False},
                   )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(#title_text="{}: Share of total district's exports".format(state_name),
                    font_color="black",
                    height=400,
                    #margin={"r":15,"t":50,"l":15,"b":5},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    geo=dict(bgcolor= 'rgba(0,0,0,0)'),)
    
    return fig, state_name


def get_dist_table(engine, geoid):

    query = '''SELECT * from (select STNAME, DESCRIPTION, VALMX / 1000000 as VALMX, VALWORLD / 1000000 as VALWORLD, TOTJOBS FROM NAFTA_MEXICO
            WHERE GEOID = :1
            ORDER BY VALMX DESC)
            WHERE ROWNUM <= 20
            '''
        
    #query = '''SELECT STNAME, DESCRIPTION, VALMX / 1000000 AS 'Value (USD Million)', (Value_mx * 100/ Value_world) AS "Mexico's share (%)", Total_Jobs AS 'Total Jobs'
        #FROM nafta_mexico 
        #WHERE GEOID = ?
        #ORDER BY Value_mx DESC LIMIT 20
        #'''
    
    df = pd.read_sql(query, engine, params=(geoid,))
    df["Mexico's share (%)"] = df['valmx'] / df['valworld'] * 100
    df.rename(columns={"valmx": "Value (USD Million)", "totjobs": "Total Jobs", "description": "Description"}, inplace=True)
    state_name = df.stname.unique()[0]
    df["Mexico's share (%)"] = df["Mexico's share (%)"].round(1)
    df['Value (USD Million)'] = df.apply(lambda x: "{:,.1f}".format(x['Value (USD Million)']), axis=1)
    df['Total Jobs'] = df.apply(lambda x: "{:,.0f}".format(x['Total Jobs']), axis=1)
    df['Rank'] = range(1, len(df) + 1)

    return df[['Rank', 'Description', 'Value (USD Million)', "Mexico's share (%)", 'Total Jobs']], state_name


def get_naics_df(engine, NAICS4):

    if NAICS4 == '00':
        #query = '''SELECT STATE_NAME AS State, CD AS Dist, sum(Value_mx) / 1000000 AS 'Value (USD Million)',
                #sum(Total_Jobs) AS 'Total Jobs', STATE 
                #FROM nafta_mexico 
                #GROUP BY STATE_NAME, CD
                #ORDER BY 3 Desc
                #'''
                
        query = '''select stname, cd, sum(valmx) / 1000000 as valmx, sum(totjobs) as totjobs, st
            from nafta_mexico
            group by stname, st, cd
            order by 3 desc'''
                
        df = pd.read_sql(query, engine)
        df.rename(columns={"stname": "State", "cd": "Dist", "valmx": "Value (USD Million)", "totjobs": "Total Jobs"}, inplace=True)

        df["District's share (%)"] = df['Value (USD Million)'] * 100 / df['Value (USD Million)'].sum()
        df = df.head(20)
        prod_name = 'Total, all sectors'

    else:
        #query = '''SELECT Description, STATE_NAME AS State, CD AS Dist, Value_mx / 1000000 AS 'Value (USD Million)',
                    #(Value_mx * 100) / (SELECT sum(Value_mx) FROM nafta_mexico 
                    #WHERE NAICS4 = ? GROUP BY NAICS4) As "District's share (%)", Total_Jobs AS 'Total Jobs', STATE 
                #FROM nafta_mexico 
                #WHERE NAICS4 = ?
                #ORDER BY Value_mx Desc
                #LIMIT 20'''
                
        query = '''SELECT * FROM (SELECT description, stname, CD, valmx / 1000000 AS valmx, totjobs, 
                        ROUND(valmx * 100 / (SELECT sum(valmx) FROM nafta_mexico WHERE NAICS = :1), 2) sh
                    FROM nafta_mexico 
                    WHERE NAICS = :2
                    ORDER BY valmx Desc) WHERE rownum <= 20'''

        df = pd.read_sql(query, engine, params=(NAICS4,NAICS4))
        df = df.head(20)
        df.rename(columns={"stname": "State", "cd": "Dist", "valmx": "Value (USD Million)", "totjobs": "Total Jobs", "sh":"District's share (%)"}, inplace=True)
        prod_name = df.description.unique()[0]
    
    df['Value (USD Million)'] = df.apply(lambda x: "{:,.1f}".format(x['Value (USD Million)']), axis=1)
    df["District's share (%)"] = df["District's share (%)"].round(1)
    df['Total Jobs'] = df.apply(lambda x: "{:,.0f}".format(x['Total Jobs']), axis=1)
    df['LastDigit'] = df['Dist'].str.strip().str[-1]
    df['last'] = np.where(df.LastDigit == '1', 'st', 
                       np.where(df.LastDigit == '2', 'nd', np.where(df.LastDigit == '3', 'rd', 'th')))
    df.insert(0, "District", 
        df[['State','Dist', 'last']].apply(lambda x : '{} {}{}'.format(x['State'], int(x['Dist']), x['last']), axis=1))
    df['Rank'] = range(1, len(df) + 1)

    return df[["Rank","District", "Value (USD Million)", "District's share (%)", "Total Jobs"]], prod_name

def get_district_boxes(engine, geoid):
    '''
    '''
    
    query = '''SELECT sum(VALMX) AS Value_mx, sum(VALWORLD) AS Value_world, sum(TOTJOBS) AS Total_Jobs, avg(year) AS year
        FROM nafta_mexico
        WHERE GEOID = :1
        '''
        
    df = pd.read_sql(query, engine, params=(geoid,))
    df['Share'] = (df.value_mx * 100) / df.value_world

    val = (df.value_mx.values[0] / 1000000)
    share = df.Share.values[0]
    jobs = df.total_jobs.values[0]
    year = df.year.values[0]

    share_rv = '{:,.0f}%'.format(share)
    value_rv = 'US ${:,.0f} million'.format(val)
    jobs_rv = '{:,.0f} jobs'.format(jobs)

    return share_rv, value_rv, jobs_rv, year

def get_prod_boxes(engine, NAICS4):

    if NAICS4 == '00':
        query = '''SELECT SUM(VALMX) / 1000000 AS Value_mx, SUM(TOTJOBS) AS Total_Jobs
            FROM nafta_mexico'''
        df = pd.read_sql(query, engine)
        df['share'] = 100
        
        val = df.value_mx.values[0]
        share = df.share.values[0]
        jobs = df.total_jobs.values[0]

    else:
        
        query1 = '''SELECT SUM(VALMX) / 1000000 tot_val FROM nafta_mexico'''
        tot = pd.read_sql(query1, engine)
        
        query = '''SELECT SUM(VALMX) / 1000000 AS value_mx, SUM(TOTJOBS) AS total_jobs
            FROM nafta_mexico 
            WHERE NAICS = :1'''
        df = pd.read_sql(query, engine, params=(NAICS4,))
    
        val = df.value_mx.values[0]
        share = val * 100 / tot.tot_val.values[0]
        jobs = df.total_jobs.values[0]

    share_rv = '{:,.0f}%'.format(share)
    value_rv = 'US ${:,.0f} million'.format(val)
    jobs_rv = '{:,.0f} jobs'.format(jobs)

    return share_rv, value_rv, jobs_rv
    

