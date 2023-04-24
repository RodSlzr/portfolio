import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import json
import numpy as np
from statsmodels.tsa.seasonal import STL
from plotly.subplots import make_subplots
#from sklearn.metrics import mean_absolute_error

TABLES = {'imp' : {2: 'CENSUS_COUNTRY_IMP_H2', 4:'CENSUS_COUNTRY_IMP_H4', 6:'CENSUS_COUNTRY_IMP'}, 
    'exp' : {2: 'CENSUS_COUNTRY_EXP_H2', 4:'CENSUS_COUNTRY_EXP_H4', 6:'CENSUS_COUNTRY_EXP_H6'}}
COLUMNS = {'imp': {'val_mo': 'GEN_VAL_MO', 'val_yr': 'GEN_VAL_YR', 'com_code': 'I_COMMODITY', 'com_desc': 'I_COMMODITY_SDESC'}, 
    'exp': {'val_mo': 'ALL_VAL_MO'  , 'val_yr': 'ALL_VAL_YR', 'com_code': 'E_COMMODITY', 'com_desc': 'E_COMMODITY_SDESC'}}

def figure_format(fig, title, source, legend):
    '''
    adds format to figure object
    '''
        
    fig.update_layout( 
        title=title,
        font_color="black",
        xaxis=dict(
            showline=True,
            showgrid=False,
            #showticklabels=True,
            #tickmode='linear',
            #linecolor='#316395',
            linecolor='black',
            linewidth=1,
            ticks='outside',
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            #linecolor='#316395',
            linecolor='black',
            linewidth=1,
            showticklabels=True,
            ticks='outside'
            #tickformat = ",d",
        ),
        showlegend=legend,
        #legend=dict(
        #orientation="h",
        #xanchor="center",
        #x=.5,
        #yanchor="top",
        #y=-0.1,
        #),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #margin={"r":60,"t":60,"l":60,"b":60},
        #height=450,
        annotations=[
        dict(
            x=0,
            y=-0.48,
            showarrow=False,
            text=source,
            xref="paper",
            yref="paper",
            font_size=10,
            font_color='gray'
        )]
    )

def get_top10_bar(engine, com_type, hs, time):
    
    if hs == '-':
        query = """select * from (SELECT CTY_NAME, CTY_CODE, sum({}) VAL_MO, sum({}) VAL_YR
                from {}
                WHERE TIME = :1 and CTY_NAME != :2
                GROUP BY CTY_NAME, CTY_CODE
                ORDER BY VAL_MO DESC)
                WHERE rownum <= 10
                """.format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], TABLES[com_type][2])
        
        top10 = pd.read_sql(query, con=engine, params=(time, 'TOTAL FOR ALL COUNTRIES'))
        top10['com_desc'] = 'Total, all commodities'
        top10['com_code'] = '-'

    else:
        query = """select * from (SELECT CTY_NAME, CTY_CODE, {} COM_DESC, {} VAL_MO, {} VAL_YR, time
                from {}
                WHERE {} = :1 and TIME = :2 and CTY_NAME != :3 and {} != 0
                ORDER BY VAL_MO DESC)
                WHERE rownum <= 10
                """.format(COLUMNS[com_type]['com_desc'], COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], 
                    TABLES[com_type][len(hs)], COLUMNS[com_type]['com_code'], COLUMNS[com_type]['val_mo'])
    
        top10 = pd.read_sql(query, con=engine, params=(hs, time, 'TOTAL FOR ALL COUNTRIES'))
    
    countries = list(top10.cty_code.unique())

    fig = px.bar(top10.sort_values(by='val_mo', ascending=True), 
        y='cty_name', 
        x='val_mo', 
        text='val_mo',
        #width=400,
        )
    
    verb = 'Importing' if com_type == 'imp' else 'Exporting'
    title = 'Top 10 {} Countries ({}) <br><sup>{}</sup>'.format(verb, time, top10.com_desc.unique()[0])
    source = 'Source: U.S. Census Bureau'
    figure_format(fig, title, source, False)
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside', marker_color='#111d5d', cliponaxis = False)
    fig.update_xaxes(title='USD')
    fig.update_yaxes(title=None)
    #fig.update_layout(margin=dict(l=100, r=150),)

    return fig, countries

def get_map(engine, com_type, hs, time, ctys):

    if hs == '-':
        query = """SELECT CTY_NAME, CTY_CODE, sum({}) VAL_MO, sum({}) VAL_YR
                from {}
                WHERE TIME = :1 and CTY_NAME != :2 and {} != 0
                GROUP BY CTY_NAME, CTY_CODE
                ORDER BY VAL_MO DESC
                """.format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], TABLES[com_type][2], 
                COLUMNS[com_type]['val_mo'])

        df = pd.read_sql(query, con=engine, params=(time, 'TOTAL FOR ALL COUNTRIES'))
        df['com_desc'] = 'Total, all commodities'
        df['com_code'] = '-'

    else:
        query = """SELECT CTY_NAME, CTY_CODE, {} VAL_MO, {} VAL_YR, {} COM_CODE, {} COM_DESC              
                from {}
                WHERE  {} = :1 and TIME = :2 and CTY_NAME != :3 and {} != 0
                ORDER BY VAL_MO DESC
                """.format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], COLUMNS[com_type]['com_code'], COLUMNS[com_type]['com_desc'],
                TABLES[com_type][len(hs)], COLUMNS[com_type]['com_code'], COLUMNS[com_type]['val_mo'])
    
        df = pd.read_sql(query, con=engine, params=(hs, time, 'TOTAL FO   R ALL COUNTRIES'))

    df['cty_low'] = df['cty_name'].str.lower()
    ctys['cty_low'] = ctys.Country.str.lower()
    merged = df.merge(ctys[['cty_low', 'Alpha-3 code']], on='cty_low', how='inner')


    fig = go.Figure(data=go.Choropleth(
            locations = merged['Alpha-3 code'],
            z = merged["val_mo"],
            text = merged['cty_name'],
            colorscale = 'Plasma',
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '$',
            colorbar_title = 'val_mo',
            ))

    fig.update_geos(projection_type="natural earth")
    fig.update_layout(margin={"r":5,"t":0,"l":5,"b":5},
        font_color="black",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    geo=dict(bgcolor= 'rgba(0,0,0,0)'),)
    title = 'Map Importing Countries ({}) <br><sup>{}</sup>'.format(time, merged.com_desc.unique()[0])
    source = 'Source: U.S. Census Bureau'
    #figure_format(fig, title, source, False)

    return fig, merged.com_desc.unique()[0]

def get_top10_lines(engine, com_type, hs, countries):

    if hs == '-':
        query = """SELECT CTY_NAME, CTY_CODE, sum({}) VAL_MO, sum({}) VAL_YR, TIME
            from {}
            WHERE CTY_CODE in """.format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], TABLES[com_type][2])
        q2= "("
        q3 =" GROUP BY CTY_NAME, CTY_CODE, TIME"
        params = tuple()
    
    else:
        query = """SELECT CTY_NAME, CTY_CODE, {} VAL_MO, {} VAL_YR, {} COM_DESC, TIME
            from {}
            WHERE {} = :1 and CTY_CODE in 
                """.format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], COLUMNS[com_type]['com_desc'], TABLES[com_type][len(hs)], COLUMNS[com_type]['com_code'])
        q2 = "("
        q3 = ""
        params = (hs,)

    for i, code in enumerate(countries):
        q2 += ':{}, '.format(i+2)
        params += (code,)

    q2 = q2[:-2] + ')'
    top = pd.read_sql(query + q2 + q3, con=engine, params=params)
    if hs == '-':
        top['com_desc'] = 'Total, all commodities'

    fig = go.Figure()

    for i, code in enumerate(countries):
        df = top[top.cty_code == code].sort_values(by='time')
        fig.add_trace(go.Scatter(x=df['time'], y=df['val_mo'],
                    mode='lines',
                    name=df.cty_name.unique()[0]))
    
    verb = 'Importing' if com_type == 'imp' else 'Exporting'
    title = 'Top 10 {} Countries <br><sup>{}</sup>'.format(verb, top.com_desc.unique()[0])
    source = 'Source: U.S. Census Bureau'
    figure_format(fig, title, source, True)

    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    return fig


def cty_line(engine, com_type, hs, cty):
    '''
    '''

    if hs == '-':
        query = """SELECT CTY_NAME, CTY_CODE, TIME, sum(GEN_VAL_MO) GEN_VAL_MO, sum(GEN_VAL_YR) GEN_VAL_YR
            from CENSUS_COUNTRY_IMP_H2
            WHERE CTY_CODE = :cty_code GROUP BY CTY_NAME, CTY_CODE, TIME order by time desc"""

        df = pd.read_sql(query, con=engine, params=(cty, ))
        com_name = 'Total, all commodities'

    else:
        query = """SELECT I_COMMODITY_SDESC, CTY_NAME, CTY_CODE, TIME, GEN_VAL_MO, GEN_VAL_YR
            from {}
            WHERE CTY_CODE = :1 and I_COMMODITY = :2 
            order by time desc """.format(TABLES[com_type][len(hs)])

        df = pd.read_sql(query, con=engine, params=(cty, hs))
        com_name = df.i_commodity_sdesc.unique()[0]

    cty_name = df.cty_name.unique()[0]
    df['MA5'] = df['gen_val_mo'].rolling(5).mean()
    df['MA12'] = df['gen_val_mo'].rolling(12).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['time'], y=df['gen_val_mo'],
                    mode='lines',
                    name='Total Value',
                    line=dict(color='purple', width=3),
                    marker=dict(size=8),))

    fig.add_trace(go.Scatter(
        x=df['time'], 
        y=df['MA5'],
        name='Moving Average 5 months',
        line=dict(color='orange', width=3, dash='dot'),
        marker=dict(size=8),    
        ))

    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['MA12'],
        name='Moving Average 12 months',
        line=dict(color='blue', width=3, dash='dot'),
        marker=dict(size=8),
    ))


    title = 'Imports from {} <br><sup>{}</sup>'.format(cty_name, com_name)
    source = 'Source: U.S. Census Bureau'
    figure_format(fig, title, source, True)

    return fig



def data_series(engine, com_type, hs, cty):

    if hs == '-':
        query = """SELECT CTY_NAME, TIME, sum({}) VAL_MO
            from {}
            WHERE CTY_CODE = :cty_code 
            GROUP BY CTY_NAME, TIME order by time desc""".format(COLUMNS[com_type]['val_mo'],TABLES[com_type][2])

        df = pd.read_sql(query, con=engine, params=(cty, ))
        com_name = 'Total, all commodities'

    else:
        query = """SELECT {} COM_DESC, CTY_NAME, TIME, {} VAL_MO
            from {}
            WHERE CTY_CODE = :1 and {} = :2 
            order by time desc """.format(COLUMNS[com_type]['com_desc'], COLUMNS[com_type]['val_mo'], TABLES[com_type][len(hs)], COLUMNS[com_type]['com_code'])

        df = pd.read_sql(query, con=engine, params=(cty, hs))
        com_name = df.com_desc.unique()[0]
    
    country = df.cty_name.unique()[0]

    df['time'] = pd.to_datetime(df['time'], infer_datetime_format=True)
    df = df.set_index('time')

    return df, com_name, country


def series_decompose(data, com_name, com_type, cty):
    '''
    Decompose series into trend, seasibality and error
    '''
    
    #df = data.asfreq(pd.infer_freq(data.index))
    df = data
    stl = STL(df['val_mo'], period=12)
    result = stl.fit()
    seasonal, trend, resid = result.seasonal, result.trend, result.resid
    
    fig = make_subplots(rows=4, cols=1)

    fig.append_trace(go.Scatter(
        x=df.index, y=df['val_mo'],
        mode='lines',
        name='Original Series',
    ), row=1, col=1)


    fig.append_trace(go.Scatter(
        x=trend.index, y=trend,
        mode='lines',
        name='Trend',
    ), row=2, col=1)

    fig.append_trace(go.Scatter(
        x=seasonal.index, y=seasonal,
        mode='lines',
        name='Seasonal',
    ), row=3, col=1)

    fig.append_trace(go.Scatter(
        x=resid.index, y=resid,
        mode='markers',
        name='Residual',
    ), row=4, col=1)
    
    verb  = 'Imports' if com_type == 'imp' else 'Exports'
    country = data.cty_name.unique()[0]
    title = 'Time series decomposition<br><sup>{} from {}: {}</sup>'.format(verb, country, com_name)
    #source = 'Source: U.S. Census Bureau'
    fig.update_layout( 
        font_color="black", title=title,paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=900,)

    fig.update_xaxes(showline=True, linecolor='black',linewidth=1, ticks='outside')
    fig.update_yaxes(showline=True, linecolor='black',linewidth=1, ticks='outside')
    
    return fig, trend, seasonal, resid

def anomalies(data, trend, seasonal, resid, com_name, com_type, cty):
    '''
    plot anomalies in data series
    '''
    
    estimated = trend + seasonal

    resid_mu = resid.mean()
    resid_dev = resid.std()

    lower = resid_mu - 2*resid_dev
    upper = resid_mu + 2*resid_dev

    anomalies = data['val_mo'][(resid < lower) | (resid > upper)]
    
    fig = go.Figure()


    fig.add_trace(go.Scatter(x=data.index, y= data['val_mo'],
                    mode='lines',
                    name='Original Series',
                    line=dict(color='purple', width=3),
                    marker=dict(size=8),))

    fig.add_trace(go.Scatter(x=data.index, y= estimated,
                    mode='lines',
                    name='Estimated',
                    line=dict(color='blue', width=3, dash='dash'),
                    marker=dict(size=8),))

    fig.add_trace(go.Scatter(x=anomalies.index, y= anomalies,
                    mode='markers',
                    name='Anomalies',
                    line=dict(color='red', width=3),
                    marker=dict(size=8),))
    
    country = data.cty_name.unique()[0]
    verb  = 'Imports' if com_type == 'imp' else 'Exports'
    title = 'Anomalies: {} from {} <br><sup>{}</sup>'.format(verb, country, com_name)
    source = 'Source: U.S. Census Bureau'
    figure_format(fig, title, source, True)
    
    return fig
    
# def moving_avg(data, com_name, window, scale=1.96):
#     '''
#     '''

#     cty_name = data.cty_name.unique()[0]
#     series = data['gen_val_mo']
#     series = series.to_frame()
#     rolling_mean = series.rolling(window=window).mean()

#     # Plot confidence intervals for smoothed values
#     mae = mean_absolute_error(series[window:], rolling_mean[window:])
#     deviation = np.std(series[window:] - rolling_mean[window:])
#     lower_bond = rolling_mean - (mae + scale * deviation)
#     upper_bond = rolling_mean + (mae + scale * deviation)

#     #find abnormal values
#     anomalies = pd.DataFrame(index=series.index, columns=series.columns)
#     anomalies[series<lower_bond] = series[series<lower_bond]
#     anomalies[series>upper_bond] = series[series>upper_bond]

#     fig = go.Figure()
    
#     fig.add_trace(go.Scatter(x=series.index, y=series.iloc[:,0],
#                     mode='lines',
#                     name='Total Value',
#                     line=dict(color='purple', width=3),
#                     marker=dict(size=8),))
    
#     fig.add_trace(go.Scatter(
#         x=series.index, 
#         y=rolling_mean.iloc[:,0],
#         name='Moving Average 6 months',
#         line=dict(color='orange', width=3, dash='dot'),
#         marker=dict(size=8),    
#         ))
    
#     fig.add_trace(go.Scatter(
#         x=series.index,
#         y=upper_bond.iloc[:,0],
#         name='Upper CI',
#         line=dict(color='blue', width=2, dash='dash'),
#         marker=dict(size=8),
#     ))
    
#     fig.add_trace(go.Scatter(
#         x=series.index,
#         y=lower_bond.iloc[:,0],
#         name='Lower CI',
#         line=dict(color='blue', width=2, dash='dash'),
#         marker=dict(size=8),
#     ))
    
#     fig.add_trace(go.Scatter(mode='markers',
#         x=series.index,
#         y=anomalies.iloc[:,0],
#         name='Anomalies',
#         marker=dict(size=10, color='blue'),
#     ))
    
#     title = 'Imports from {} <br><sup>{}</sup>'.format(cty_name, com_name)
#     source = 'Source: U.S. Census Bureau'
#     figure_format(fig, title, source, True)
    
#     return fig

# def exponential_smoothing(series, alpha):
#     """
#         series - dataset with timestamps
#         alpha - float [0.0, 1.0], smoothing parameter
#     """

#     result = [series[0]] # first value is same as series
#     for n in range(1, len(series)):
#         result.append(alpha * series[n] + (1 - alpha) * result[n-1])
#     return result


# def plotExponentialSmoothing(data, com_name, alpha=0.02, scale=1.96):

#     """
#         Plots exponential smoothing with different alphas
        
#         series - dataset with timestamps
#         alphas - list of floats, smoothing parameters
#     """
    
#     cty_name = data.cty_name.unique()[0]
#     series = data['gen_val_mo']

#     rolling_mean = exponential_smoothing(series, alpha)
#     series = series.to_frame()
#     rolling_mean = pd.DataFrame(rolling_mean, index=series.index, columns=series.columns)

#     # Plot confidence intervals for smoothed values
#     mae = mean_absolute_error(series, rolling_mean)
#     deviation = np.std(series - rolling_mean)
#     lower_bond = rolling_mean - (mae + scale * deviation)
#     upper_bond = rolling_mean + (mae + scale * deviation)

#     #find abnormal values
#     anomalies = pd.DataFrame(index=series.index, columns=series.columns)
#     anomalies[series<lower_bond] = series[series<lower_bond]
#     anomalies[series>upper_bond] = series[series>upper_bond]

#     fig = go.Figure()
    
#     fig.add_trace(go.Scatter(x=series.index, y=series.iloc[:,0],
#                     mode='lines',
#                     name='Total Value',
#                     line=dict(color='purple', width=3),
#                     marker=dict(size=8),))
    
#     fig.add_trace(go.Scatter(
#         x=series.index, 
#         y=rolling_mean.iloc[:,0],
#         name='Exponential Smoothing',
#         line=dict(color='orange', width=3, dash='dot'),
#         marker=dict(size=8),    
#         ))
    
#     fig.add_trace(go.Scatter(
#         x=series.index,
#         y=upper_bond.iloc[:,0],
#         name='Upper CI',
#         line=dict(color='blue', width=2, dash='dash'),
#         marker=dict(size=8),
#     ))
    
#     fig.add_trace(go.Scatter(
#         x=series.index,
#         y=lower_bond.iloc[:,0],
#         name='Lower CI',
#         line=dict(color='blue', width=2, dash='dash'),
#         marker=dict(size=8),
#     ))
    
#     fig.add_trace(go.Scatter(mode='markers',
#         x=series.index,
#         y=anomalies.iloc[:,0],
#         name='Anomalies',
#         marker=dict(size=10, color='blue'),
#     ))

#     title = 'Imports from {} <br><sup>{}</sup>'.format(cty_name, com_name)
#     source = 'Source: U.S. Census Bureau'
#     figure_format(fig, title, source, True)
    
#     return fig
