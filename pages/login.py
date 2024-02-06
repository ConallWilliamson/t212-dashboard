import dash
from dash import html, dcc, Output, Input, State, callback
import sqlite3

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H6("Please enter your username"),
    html.Div([
        "Username : ",
        dcc.Input(id='username-input', type='text')],
        style={'margin-bottom': '10px'}
    ),

    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='auth-output')
])


@callback(
    Output('auth-output', 'children'),
    Input('submit-val', 'n_clicks'),
    State('username-input', 'value'),
    prevent_initial_call=True
)
def check_user(n_clicks, username):
    # Check if the username exists in the database
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE user = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return dcc.Location(pathname='/dashboard', id='redirect-main')
    else:
        return 'User not found. Please enter a valid username.'