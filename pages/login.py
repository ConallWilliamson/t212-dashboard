import dash
from dash import html, dcc, Output, Input, State, callback
import sqlite3
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Div([
            html.H6("Please enter your username", style={'text-align': 'center'}),
            dcc.Input(id='username-input', type='text', style={'margin-bottom': '10px', 'width': '100%'}),
            html.Button('Submit', id='submit-val', n_clicks=0, style={'width': '100%'}),
            html.Div(id='auth-output'),
            # Store component to store the username
            dcc.Store(id='user-info', storage_type='session'),
            # Location component for redirecting to the dashboard page
            dcc.Location(id='url', refresh=True)
        ], style={'width': '30%'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '100vh'})
])

@callback(
    Output('auth-output', 'children'),
    Output('user-info', 'data'),
    Output('url', 'pathname'),
    Input('submit-val', 'n_clicks'),
    State('username-input', 'value'),
    prevent_initial_call=True
)
def check_user(n_clicks, username):
    if not n_clicks:
        raise PreventUpdate

    # Check if the username exists in the database
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE user = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        # If the username exists, return a success message, store the username,
        # and navigate to the dashboard page
        return f'Welcome, {username}!', {'username': username}, '/dashboard'
    else:
        # If the username doesn't exist, return an error message
        return 'User not found. Please enter a valid username.', None, None