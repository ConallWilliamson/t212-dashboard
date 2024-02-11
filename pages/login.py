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
            # Location component for redirecting to the dashboard page
            dcc.Location(id='url', refresh=True)
        ], style={'width': '30%'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '100vh'})
])

@callback(
    Output('auth-output', 'children'),
    Output('user-info', 'data', allow_duplicate=True),
    Output('url', 'pathname'),
    Output('is-logged-in', 'data'),  # Update is-logged-in store
    Input('submit-val', 'n_clicks'),
    State('username-input', 'value'),
    prevent_initial_call=True
)
def check_user(n_clicks, username):
    if not n_clicks:
        raise PreventUpdate

    # Initialize an empty dictionary to store user information
    user_info = {}

    # Check if the username exists in the database
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()

    # Fetch user information from the user table
    cursor.execute('SELECT * FROM user WHERE user = ?', (username,))
    user_result = cursor.fetchone()
    if user_result:
        # If the user exists, store username and API key
        user_info['username'] = username
        user_info['api_key'] = user_result[1]  # Assuming API key is in the second column

        # Fetch pie metadata associated with the user from the pies table
        cursor.execute('SELECT pie, pie_id, currency, url FROM pies WHERE user = ?', (username,))
        pie_results = cursor.fetchall()
        if pie_results:
            # If pies are associated with the user, store them in a list of dictionaries
            pies_info = [{'pie': row[0], 'pie_id': row[1], 'currency': row[2], 'url': row[3]} for row in pie_results]
            user_info['pies'] = pies_info

        conn.close()

        # Return success message, user info, navigate to the dashboard page, and set is-logged-in to True
        return f'Welcome, {username}!', user_info, '/dashboard', True
    else:
        conn.close()

        # If the username doesn't exist, return an error message
        return 'User not found. Please enter a valid username.', None, None, False
