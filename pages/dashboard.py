from dash import Dash, Input, Output, dcc, html, State, callback
import json
import sqlite3
import dash
from utils import *

f_subs = open('subs.json')
subs = json.load(f_subs)

f_pies = open('pies.json')
pies = json.load(f_pies)
keys = pies.keys()

dash.register_page(__name__)


layout = html.Div([
    html.H6("Please enter your username"),
    html.Div([
        "Username : ",
        dcc.Input(id='username-input', type='text')],
        style={'margin-bottom': '10px'}
    ),

    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='my-output'),

    
    # New div to contain the API key input box, initially hidden
    html.Div(id='api-key-container', style={'display': 'none'}, children=[
        html.Div([
            "API Key : ",
            dcc.Input(id='api-key-input', type='text')],
            style={'margin-top': '10px', 'margin-bottom': '10px'}
        ),
        html.Button('Submit API Key', id='submit-api-key', n_clicks=0),
        html.Div(id='api-key-output')
    ]),


    html.Button('Fetch all Pies', id='fetch-all', n_clicks=0),
    html.Div(id='available-pies'),

    dcc.Dropdown(id='pie-dropdown'),
    html.Div(id='pie-selection'),

    # New button to trigger the reweight function
    html.Button('Rebalance Pie', id='rebalance-button', n_clicks=0),
    html.Div(id='rebalance-output')

])




# Callback to handle the submission of the API key
@callback(
    Output('api-key-output', 'children'),
    Input('submit-api-key', 'n_clicks'),
    State('username-input', 'value'),
    State('api-key-input', 'value'),
    prevent_initial_call=True
)
def submit_api_key(n_clicks, username, api_key):
    # Check if the user already has an API key stored
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM user WHERE user = ?', (username,))
    result = cursor.fetchone()

    if result is None:
        # If the user doesn't have an API key stored, insert the new API key
        cursor.execute('INSERT INTO user (user, api_key) VALUES (?, ?)', (username, api_key))
        conn.commit()
        conn.close()
        return f'API key submitted for user "{username}".'
    else:
        conn.close()
        return f'User "{username}" already has an API key stored: {result[0]}'

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

