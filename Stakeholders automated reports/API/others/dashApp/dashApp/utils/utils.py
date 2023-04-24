import pandas as pd
from sqlalchemy import text
from dash import html
from dash import dcc

TABLES = {'imp' : {2: 'CENSUS_COUNTRY_IMP_H2', 4:'CENSUS_COUNTRY_IMP_H4', 6:'CENSUS_COUNTRY_IMP'}, 
    'exp' : {2: 'CENSUS_COUNTRY_EXP_H2', 4:'CENSUS_COUNTRY_EXP_H4', 6:'CENSUS_COUNTRY_EXP_H6'}}
COLUMNS = {'imp': {'val_mo': 'GEN_VAL_MO', 'val_yr': 'GEN_VAL_YR', 'com_code': 'I_COMMODITY', 'com_desc': 'I_COMMODITY_SDESC'}, 
    'exp': {'val_mo': 'ALL_VAL_MO'  , 'val_yr': 'ALL_VAL_YR', 'com_code': 'E_COMMODITY', 'com_desc': 'E_COMMODITY_SDESC'}}

def df_to_table(df):
    
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])]
        + [
            html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ]
    )

def get_dropdown(engine, parent):
    '''
    '''

    query = text("SELECT Desc, Code FROM hs_codes WHERE Code_Parent = :code_p")
    result = engine.execute(query, code_p=parent)
    result_as_list = result.fetchall()

    return result_as_list

def get_dropdown_by_level(engine, com_type, level):
    '''
    '''

    if com_type == 'imp':
        q = "SELECT NAME, CODE FROM hs_codes WHERE HS = :level_num ORDER BY NAME"
    else:
        q = "SELECT NAME, CODE FROM hs_codes_exp WHERE HS = :level_num ORDER BY NAME"

    query = text(q)
    result = engine.execute(query, level_num=level)
    result_as_list = result.fetchall()

    return result_as_list

def get_cty_dropdown(engine, com_type, comm_code):
    '''
    '''
    if comm_code == '-':
        q = """SELECT DISTINCT cty_name, cty_code 
        FROM {} ORDER BY cty_name""".format(TABLES[com_type][2])
        query = text(q)
        result = engine.execute(query)
    else:
        q = """SELECT DISTINCT cty_name, cty_code 
        FROM {} WHERE {} = :comm_code 
        ORDER BY cty_name""".format(TABLES[com_type][len(comm_code)], COLUMNS[com_type]['com_code'])

        query = text(q)
        result = engine.execute(query, comm_code=comm_code)
        
    result_as_list = result.fetchall()

    return result_as_list

def get_naics_labels(engine):
    '''
    '''

    #query = text('SELECT DISTINCT NAICS4, Description FROM nafta_mexico ORDER BY Description')
    query = text('SELECT DISTINCT NAICS, DESCRIPTION FROM nafta_mexico ORDER BY DESCRIPTION')
    result = engine.execute(query)
    codes = result.fetchall()
    labels = [{'label':'{}-{}'.format(code, name), 'value':code} for code, name in codes]
    labels = [{'label': 'Total, all sectors', 'value': '00'}] + labels

    return labels

def get_districts(engine):
    '''
    '''

    #query = text('SELECT DISTINCT CD, STATE_NAME, GEOID FROM nafta_mexico')
    query = text('SELECT DISTINCT CD, STNAME, GEOID FROM nafta_mexico')
    result = engine.execute(query)
    codes = result.fetchall()

    rv = [{'label':'{}-{}'.format(code, name), 'value':geoid} for code, name, geoid in codes]
    
    return rv

def val_month_year(engine, com_type, hs, time):
    '''
    Returns monthly and yearly value for the indicator tab
    '''

    if hs == '-':
        query = """SELECT sum({}) VAL_MO, sum({}) VAL_YR  FROM {} 
            WHERE TIME = :time and CTY_NAME = :cty GROUP BY CTY_CODE""".format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], TABLES[com_type][2])
        query_text = text(query)
        result = engine.execute(query_text, time=time , cty='TOTAL FOR ALL COUNTRIES')
    else:
        query = text("SELECT {} VAL_MO, {} VAL_YR FROM {} WHERE {} = :com and TIME = :time and CTY_NAME = :cty".format(COLUMNS[com_type]['val_mo'], COLUMNS[com_type]['val_yr'], TABLES[com_type][len(hs)], COLUMNS[com_type]['com_code']))
        result = engine.execute(query, com=hs, time=time, cty='TOTAL FOR ALL COUNTRIES')

    val_month, val_yr = result.fetchall()[0]

    return round(val_month/1000000, 1), round(val_yr/1000000, 1)

def get_max_date(engine):
    query = 'select max(TIME) from census_country_imp_h2'
    result = engine.execute(query)
    time = result.fetchone()[0]

    return time

