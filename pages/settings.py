import dash
from dash import dcc, html, Input, Output, State, callback
import sqlite3
from dash.exceptions import PreventUpdate

dash.register_page(__name__)


layout = html.Div([
    html.H4(id='user-settings-header'),
    # New div to contain the API key input box, initially hidden
    html.Div(id='api-key-container', children=[
        html.Div([
            "API Key : ",
            dcc.Input(id='api-key-input', type='text')],
            style={'margin-top': '10px', 'margin-bottom': '10px'}
        ),
        html.Button('Submit API Key', id='submit-api-key', n_clicks=0),
        html.Div(id='api-key-output')
    ])
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
    Output('user-settings-header', 'children'),
    Input('user-info', 'data'),
    prevent_initial_call = False
)
def update_user_settings_header(user_data):
    if user_data is not None:
        #print('stored user')
        username = user_data['username']
        return f"User Settings for {username}"
    else:
        print('not storing user')
        raise PreventUpdate