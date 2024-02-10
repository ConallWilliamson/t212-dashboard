from dash import Dash, Input, Output, dcc, html, State, callback
import json
import sqlite3
import dash
import dash_bootstrap_components as dbc
from utils import *

f_subs = open('subs.json')
subs = json.load(f_subs)

f_pies = open('pies.json')
pies = json.load(f_pies)
keys = pies.keys()

dash.register_page(__name__)


layout = html.Div([
    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.Col(dbc.NavbarBrand("Navbar")),
            dbc.NavLink("Settings", href="/settings"),
            # You can add more navigation links here if needed
        ],
        fluid = True),
        color="primary",
        dark=True
    ),



    html.Button('Fetch all Pies', id='fetch-all', n_clicks=0),
    html.Div(id='available-pies'),

    dcc.Dropdown(id='pie-dropdown'),
    html.Div(id='pie-selection'),

    # New button to trigger the reweight function
    html.Button('Rebalance Pie', id='rebalance-button', n_clicks=0),
    html.Div(id='rebalance-output')

])






@callback(
    Output('pie-dropdown', 'options'),
    Input('fetch-all', 'n_clicks'),
    State('username-input', 'value'),
    prevent_initial_call=True
)
def update_pie_dropdown(n_clicks, username):
    # Check the SQLite database for pies associated with the username
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT pie FROM pies WHERE user = ?', (username,))
    pie_options = [{'label': pie[0], 'value': pie[0]} for pie in cursor.fetchall()]
    conn.close()

    return pie_options

@callback(
    Output('pie-selection', 'children'),
    Input('pie-dropdown', 'value'),
    State('username-input', 'value'),
    prevent_initial_call=True
)    
def confirm_pie_selection(pie_dropdown, username):
    # Check the SQLite database for information about the selected pie
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT pie_id, currency, url FROM pies WHERE user = ? AND pie = ?', (username, pie_dropdown))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return f'No information found for pie "{pie_dropdown}" belonging to user "{username}".'
    else:
        pie_id, currency, url = result
        return 'You have selected "{}". This has a pie ID of "{}". You have an API key for user "{}". This pie will rebalance based on the following URL: "{}", and has a currency of "{}".'.format(pie_dropdown, pie_id, username, url, currency)

# Callback to handle the reweighting when the "Rebalance Pie" button is clicked
@callback(
    Output('rebalance-output', 'children'),
    Input('rebalance-button', 'n_clicks'),
    State('username-input', 'value'),
    State('pie-dropdown', 'value'),
    prevent_initial_call=True
)
def perform_reweighting(n_clicks, username, selected_pie):
    # Fetch the necessary information from the database
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT pie_id, currency, url FROM pies WHERE user = ? AND pie = ?', (username, selected_pie))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return f'No information found for pie "{selected_pie}" belonging to user "{username}".'
    else:
        pie_id, currency, url = result
        # Call the reweight function with the fetched information and globally defined subs
        response = reweight(username, url, pie_id, currency, subs)
        return f'Reweighting for pie "{selected_pie}" initiated. Response: {response.text}'

