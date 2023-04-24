import dash
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine

#conn = create_engine('sqlite:///macro.db')

oracle_connection_string = 'oracle+cx_oracle://{username}:{password}@{hostname}:{port}/{database}'
engine = create_engine(
    oracle_connection_string.format(
        username='TEMEC',
        password='dA1809Bj',
        hostname='10.100.30.16',
        port='1521',
        database='SINEC1',
    )
)

app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='./assets/', external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server