import dash
from dash import dcc, html, Input, Output, State, ALL, callback
import sqlite3
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

layout = html.Div([
    html.H4(id='user-settings-header'),
    
    # Display the API key
    html.Div(id='api-key-container'),

    html.Br(),
    
    # Display the pie information
    html.Div(id='pies-container'),

    # Hidden div to store updated user data
    html.Div(id='updated-user-info', style={'display': 'none'})
])

# Callback to update the user settings header
@callback(
    Output('user-settings-header', 'children'),
    Input('is-logged-in', 'data'),
    State('user-info', 'data'),
    prevent_initial_call=False
)
def update_user_settings_header(is_logged_in, user_data):
    if user_data is not None and 'username' in user_data:
        username = user_data['username']
        return f"User Settings for {username}"
    else:
        raise PreventUpdate

# Callback to handle the API key editing and update the database
@callback(
    [
        Output('api-key-input', 'disabled'),
        Output('api-key-input', 'style'),
        Output('edit-api-key-button', 'children'),
        Output('updated-user-info', 'children'),  # Include updated user data
    ],
    Input('edit-api-key-button', 'n_clicks'),
    State('api-key-input', 'value'),
    State('api-key-input', 'disabled'),
    State('user-info', 'data'),
    Input('is-logged-in', 'data'),
    prevent_initial_call=True
)
def toggle_edit_api_key(n_clicks, new_api_key, current_disabled, user_data, is_logged_in):
    if n_clicks is None:
        raise PreventUpdate

    new_disabled = current_disabled
    button_text = 'Edit'
    input_style = {'width': '129ch', 'margin-right': '1ch'}  # Adjust as needed
    updated_user_data = user_data

    if n_clicks % 2 == 1:
        # Enable editing
        new_disabled = False
        button_text = 'Save'

    else:
        # Disable editing
        new_disabled = True

        # Update the database with the new API key
        username = user_data['username']
        conn = sqlite3.connect('db/t212.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET api_key = ? WHERE user = ?', (new_api_key, username))
        conn.commit()
        conn.close()

        # Update the API key in the user data
        updated_user_data['api_key'] = new_api_key

    # Update the hidden div with the updated user data
    updated_user_info = dcc.Store(data=updated_user_data, id='updated-user-data')

    return (
        new_disabled,
        input_style,
        button_text,
        updated_user_info
    )

# Callback to update the API key display
@callback(
    Output('api-key-container', 'children'),
    Input('is-logged-in', 'data'),
    State('user-info', 'data'),
    prevent_initial_call=False
)
def update_api_key_container(is_logged_in, user_data):
    if user_data is not None and 'api_key' in user_data:
        api_key = user_data['api_key']
        return html.Div([
            html.Label("API Key:", style={'margin-right': '1ch'}),
            dcc.Input(id='api-key-input', value=api_key, disabled=True, style={'width': '129ch', 'margin-right': '1ch'}),
            html.Button('Edit', id='edit-api-key-button'),
        ])
    else:
        raise PreventUpdate

# Callback to update the pie information display
@callback(
    Output('pies-container', 'children'),
    Input('is-logged-in', 'data'),
    State('user-info', 'data'),
    prevent_initial_call=False
)
def update_pies_container(is_logged_in, user_data):
    if user_data is not None and 'pies' in user_data:
        pies_info = user_data['pies']
        pies_list = []
        for pie in pies_info:
            pie_id = pie['pie_id']
            pie_div = html.Div([
                html.Label(f"Pie ID:", style={'margin-right': '1ch'}),
                html.B(pie_id, style={'margin-right': '1ch'}),
                dcc.Input(id={'type': 'pie-name', 'pie_id': pie_id}, value=pie['pie'], disabled=True, style={'width': '15ch', 'margin-right': '1ch'}),
                dcc.Input(id={'type': 'pie-currency', 'pie_id': pie_id}, value=pie['currency'], disabled=True, style={'width': '6ch', 'margin-right': '1ch'}),
                dcc.Input(id={'type': 'pie-url', 'pie_id': pie_id}, value=pie['url'], disabled=True, style={'width': '100ch', 'margin-right': '1ch'}),
                html.Button('Edit', id={'type': 'edit-button', 'pie_id': pie_id}),
                
            ], id={'type': 'pie-row', 'pie_id': pie_id}, style={'margin-bottom': '1rem'})  # Add unique ID and margin
            pies_list.append(pie_div)
        return pies_list
    else:
        raise PreventUpdate
