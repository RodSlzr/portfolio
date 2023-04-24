import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

def get_box_wb(engine, country, ind_code):
    '''
    '''
    
    query = '''SELECT * FROM WB_DATA WHERE ISO = :1 AND IND_CODE = :2
        ORDER BY YEAR DESC'''
    df = pd.read_sql(query, engine, params=(country, ind_code))
    values = df['value'].values        
    val = '{:,.0f}'.format(values[0]) if ind_code == 'NY.GDP.PCAP.CD' else '{:,.1f}'.format(values[0])
    years = df['year'].values
    year = years[0]
    if val == 'nan':
        val = '{:,.0f}'.format(values[1])
        year = years[1]
        
    return val, year


def get_box_eci(engine, country):
    '''
    '''
    
    query = 'SELECT * FROM eci WHERE ISO = :1 ORDER BY YEAR DESC'
    df = pd.read_sql(query, engine, params=(country,))
    val = '# {:,.0f}'.format(df['ecirank'].values[0])
    year = df['year'].values[0]
    
    return val, year


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
            showticklabels=True,
            tickmode='linear',
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
        legend=dict(
        orientation="h",
        xanchor="center",
        x=.5,
        yanchor="top",
        y=-0.1,
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #margin={"r":60,"t":60,"l":60,"b":60},
        #height=450,
        annotations=[
        dict(
            x=0,
            y=-0.28,
            showarrow=False,
            text=source,
            xref="paper",
            yref="paper",
            font_size=10,
            font_color='gray'
        )]
    )


#def top_partners(engine, country, rgDesc):
    #'''
    #'''
    
    #query = 'SELECT * FROM comtrade_goods WHERE ISO_code = ? AND rgDesc = ?'
    #df = pd.read_sql(query, engine, params=(country, rgDesc))
    
    #world_exp = df[(df.ptTitle == 'World')]['TradeValue'].values[0]
    #top5_exp = df[(df.ptTitle != 'World')]
    #top5_exp = top5_exp.sort_values(by='TradeValue', ascending=False)[['year', 'ptTitle', 'TradeValue']].head(n = 5)
    #top5_exp['percent'] = top5_exp['TradeValue'] / world_exp
    
    #if rgDesc == 'Export':
        #color = 'crimson'
        #title = "{}: Total exports, {}".format(country, df.year.max())
    #else:
        #color = 'LightSeaGreen'
        #title = "{}: Total imports, {}".format(country, df.year.max())

    #fig = go.Figure()
    
    #fig.add_trace(go.Bar(
        #x=top5_exp['ptTitle'],
        #y=top5_exp['TradeValue'],
        #marker_color=color
        #))

    #source = 'Source: UN Comtrade Database.'

    #figure_format(fig, title, source, False)

    
    #return fig


def top_trade_df(engine, country, rgDesc):
    '''
    '''

    #query = '''SELECT * FROM (SELECT year, pt_title AS counterpart, trade_value / 1000000 AS value 
        #FROM comtrade_goods WHERE ISO = :1 AND rg_desc = :2  AND pt_title != :3
        #ORDER BY Value DESC) where rownum <= 6'''
        
    query = '''SELECT year, counterpart, value 
                FROM (SELECT year, pt_title AS counterpart, trade_value / 1000000 AS value, rank() over (order by year desc) rank
                        FROM comtrade_goods WHERE ISO = :1 AND rg_desc = :2  AND pt_title != :3
                        ORDER BY Value DESC) 
                where rank=1 and rownum <= 6'''
    
    df = pd.read_sql(query, engine, params=(country, rgDesc, 'Areas, nes'))
    df.columns = ['year', 'Counterpart', 'Value']
    year = df.year.unique()[0]
    world = df[(df.Counterpart == 'World')]['Value'].values[0]
    top5 = df[['Counterpart', 'Value']]
    top5['Share (%)'] = top5['Value'] / world * 100
    top5['Share (%)'] = top5['Share (%)'].round(1)
    top5['Value'] = df.apply(lambda x: "{:,.0f}".format(x['Value']), axis=1)
    top5['Rank'] = range(0, len(top5))

    return top5[['Rank', 'Counterpart', 'Value', 'Share (%)']], year


def balance_comtrade(engine, country, goods):
    '''
    Takes data from comtrade
    '''
    
    table = 'comtrade_series_year' if goods else 'comtrade_services_year'
    title = "{}: Balance Trade, Goods".format(country) if goods else "{}: Balance Trade, Services".format(country)

    query = '''WITH imports as
        (SELECT * FROM {} WHERE ISO = :1 AND RG_DESC = :2),
        exports as 
        (SELECT * FROM {} WHERE ISO = :3 AND RG_DESC = :4)
        select imports.year AS year, imports.TRADE_VALUE AS imp, exports.TRADE_VALUE AS exp 
        from exports join imports ON imports.year = exports.year order by year asc
        '''.format(table, table)
    
    df = pd.read_sql(query, engine, params=(country, 'Import', country, 'Export'))
    df['balance'] = df.exp - df.imp
    df['balance_b'] = df['balance']/1000000000
    df['balance_b'] = df['balance_b'].round(2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['year'],
        y=df['exp'],
        name='Goods exports',
        marker_color='#c70039'
    ))
    
    fig.add_trace(go.Bar(
        x=df['year'],
        y=df['imp'],
        name='Goods imports',
        marker_color='#111d5e'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['year'], 
        y=df['balance'],
        mode="lines+markers+text",
        name='Net Exports',
        line=dict(color='orange', width=3),
        marker=dict(size=8), 
        text=df['balance_b'],
        textposition="top center",
        textfont_size=12,
        textfont_color='orange'
    ))
    
    source = 'Source: UN Comtrade Database.'
    figure_format(fig, title, source, True)
    return fig
    

def trade_monthly(engine, country):
    
    query = ''' WITH imports as
    (SELECT * FROM comtrade_series_month WHERE ISO = :1 AND RG_DESC = :2),
    exports as
    (SELECT * FROM comtrade_series_month WHERE ISO = :3 AND RG_DESC = :4)
    SELECT imports.COM_DATE AS com_date, imports.TRADE_VALUE AS Imp, exports.TRADE_VALUE AS Exp 
    FROM imports JOIN exports ON imports.COM_DATE = exports.COM_DATE
    ORDER BY imports.COM_DATE'''

    com = pd.read_sql(query, engine, params=(country, 'Imports', country, 'Exports'))
    com['balance'] = com.exp - com.imp
    
    last_imp = com[com.com_date == com['com_date'].max()]['imp'].values[0]
    last_exp = com[com.com_date == com['com_date'].max()]['exp'].values[0]
    last_balance = last_exp - last_imp
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=com['com_date'], 
        y=com['imp'],
        mode="lines",
        name='Imports',
        marker_color='#206a5d'))

    fig.add_trace(go.Scatter(x=com['com_date'], 
        y=com['exp'],
        mode="lines",
        name='Exports',
        marker_color='#dd2c00'))

    fig.add_trace(go.Scatter(x=com['com_date'], 
        y=com['balance'],
        mode="lines",
        name='Net Exports',
        marker_color='#318fb5'))
        
    title = "{}: Monthly Balance of Trade, Goods".format(country)

    fig.update_layout(
        title=title,
        font_color="black",
    xaxis=dict(
        showgrid=False,
        showticklabels=True, 
        showline=True,
        linecolor='black',
        linewidth=1,
        ticks='outside',
        ),
    yaxis=dict(
        showgrid=False,
        showticklabels=True,
        showline=True,
        linecolor='black',
        linewidth=1,
        ticks='outside',
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        orientation="h",
        xanchor="center",
        x=.5
        ),
    annotations=[
        dict(
            x=0,
            y=-0.24,
            showarrow=False,
            text="Source: UN Comtrade Database.",
            xref="paper",
            yref="paper",
            font_size=10,
            font_color='gray'
        ),
        dict(
            x= com['com_date'].max(),
            y= last_exp,
            align="left",
            text= '{:.2f}B'.format(last_exp/1000000000),
            xanchor="right",
            yanchor="top",
            arrowhead=2,
            arrowwidth=1.3,
            bordercolor="gray",
            bgcolor="lightgray",
            opacity=0.8
        ),
        dict(
            x= com['com_date'].max(),
            y= last_imp,
            align="left",
            text= '{:.2f}B'.format(last_imp/1000000000),
            xanchor="right",
            yanchor="bottom",
            arrowhead=2,
            arrowwidth=1.3,
            bordercolor="gray",
            bgcolor="lightgray",
            opacity=0.8
        ),
        dict(
            x= com['com_date'].max(),
            y= last_balance,
            text= '{:.2f}B'.format(last_balance/1000000000),
            xanchor="right",
            arrowhead=2,
            arrowwidth=1.3,
            bordercolor="gray",
            bgcolor="lightgray",
            opacity=0.8
        )]
    )

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig


def get_imf_df(engine, country, type):
    '''
    '''
    
    query = '''select counterpart, value, year from 
                    (SELECT partner AS Counterpart, value / 1000000 AS Value, year, rank() over (order by year desc) rank
                    FROM direct_inv_fmi 
                    WHERE ISO = :1 AND ind_name = :2 ORDER BY value DESC) 
                where rank = 1 and rownum <= 6 '''
    
    if type == 'inward':
        df = pd.read_sql(query, engine, params=(country, 'Inward Direct Investment Positions'))
    else: 
        df = pd.read_sql(query, engine, params=(country, 'Outward Direct Investment Positions'))

    year = df.year.unique()[0]
    df.columns = ['Counterpart', 'Value', 'year']
    total = df[df.Counterpart == 'World'].Value.values[0]
    df['Share (%)'] = df['Value'] / total * 100
    df['Share (%)'] = df['Share (%)'].round(1)
    df = df[['Counterpart', 'Value', 'Share (%)']]
    df['Value'] = df.apply(lambda x: "{:,.0f}".format(x['Value']), axis=1)
    df['Rank'] = range(0, len(df))
    
    return df[['Rank', 'Counterpart', 'Value', 'Share (%)']], year

def inv_imf(engine, country): 

    query = '''WITH inward as 
        (SELECT * FROM inv_fmi_series WHERE ISO = :1 AND ind_name = :2),
        outward as
        (SELECT * FROM inv_fmi_series WHERE ISO = :3 AND ind_name = :4)
        SELECT inward.year AS year, inward.value AS inw, outward.value as outw 
        FROM inward join outward ON inward.year = outward.year ORDER BY year
        '''
    
    df = pd.read_sql(query, engine, params=(country, 'Inward Direct Investment Positions', country, 'Outward Direct Investment Positions'))
    df['net'] = df['inw'] - df['outw']
    df['text'] = df['net'] / 1000000000
    df['text'] = df['text'].round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['year'],
        y=df['inw'],
        name='Inward Direct Investment Positions',
        marker_color='#3b2e5a'
    ))
    
    fig.add_trace(go.Bar(
        x=df['year'],
        y=df['outw'],
        name='Outward Direct Investment Positions',
        marker_color='#4ea0ae'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['year'], 
        y=df['net'],
        mode="lines+markers+text",
        name='Net Direct Investment Positions',
        line=dict(color='#ed6663', width=3),
        marker=dict(size=8), 
        text=df['text'],
        textposition="top center",
        textfont_size=12,
        textfont_color='#ed6663',
    ))
    
    source = 'Source: Coordinated Direct Investment Survey (CDIS), IMF.'
    title = "{}: Direct Investment Positions".format(country)
    figure_format(fig, title, source, True)
    
    return fig