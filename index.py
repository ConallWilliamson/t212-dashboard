from dash import Dash, Input, Output, dcc, html, State, callback
import json
import requests
import sqlite3
import pandas as pd

f_subs = open('subs.json')
subs = json.load(f_subs)

f_pies = open('pies.json')
pies = json.load(f_pies)
keys = pies.keys()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
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


# Callback to handle the initial submission and show/hide the API key input box
@callback(
    [Output('my-output', 'children'),
     Output('api-key-container', 'style')],
    Input('submit-val', 'n_clicks'),
    State('username-input', 'value'),
    prevent_initial_call=True
)
def check_user(n_clicks, username):
    # Check the SQLite database for the API key associated with the username
    conn = sqlite3.connect('db/t212.db')
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM user WHERE user = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        # If the user doesn't have an API key stored, show the API key input box
        return f'No API key found for user "{username}".', {'display': 'block'}
    else:
        # If the user has an API key stored, hide the API key input box
        return f'API key found for user "{username}": {result[0]}', {'display': 'none'}

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

def get_instruments(key):
    instruments_headers = {
      "Authorization": key
  }
    instruments_response = requests.get("https://live.trading212.com/api/v0/equity/metadata/instruments", headers=instruments_headers)
    return(instruments_response)

def get_all_pies(key):
    print(key)
    url = "https://live.trading212.com/api/v0/equity/pies"
    headers = {"Authorization": key}
    response = requests.get(url, headers=headers)
    return(response)

def reweight(user, url, id, currency, subs):
  conn = sqlite3.connect('db/t212.db')
  cursor = conn.cursor()
  cursor.execute('SELECT api_key FROM user WHERE user = ?', (user,))
  key = cursor.fetchone()[0]
  conn.close()

  df = pd.read_excel(url)
  df = df.drop(df.index[0:4])
  new_header = df.iloc[0] #grab the first row for the header
  df.columns = new_header #set the header row as the df header
  df = df.drop(df.index[0]).reset_index(drop=True)
  df = df.drop(df.index[101:]).reset_index(drop=True)

  for sub in subs['subs']:
    print(sub['Name_Sub'])
    df.loc[df['ISIN'] == sub['ISIN'], ['Full name', 'ISIN']]= [sub['Name_Sub'], sub['ISIN_Sub']]

  instruments_headers = {
      "Authorization": key
  }
  instruments_response = requests.get("https://live.trading212.com/api/v0/equity/metadata/instruments", headers=instruments_headers)
  instruments_data_df  = pd.DataFrame(instruments_response.json())
  merged = df.merge(instruments_data_df, how = 'left', left_on = 'ISIN', right_on = 'isin')
  local_currency_df = merged[merged['currencyCode'] == currency].reset_index(drop=True)
  pie_candidates = local_currency_df[0:50].copy()
  #normalise remaining constituents so that they sum to 1
  pie_candidates['Weight'] = (pie_candidates['Weight']/sum(pie_candidates['Weight'])).apply(lambda x: round(x, 6))
  pie_candidates_dict = dict(zip(pie_candidates['ticker'], pie_candidates['Weight']))
  
  #circumvent floating point division problems
  int_dict = dict.fromkeys(pie_candidates_dict)
  for dict_key in pie_candidates_dict.keys():
    int_dict[dict_key] = int(pie_candidates_dict[dict_key] * 1000)
  print(sum(int_dict.values()))
  
  remainder = 1000 - sum(int_dict.values())
  
  while(remainder != 0):
    min_key = min(int_dict, key=int_dict.get)
    max_key = max(int_dict, key=int_dict.get)
    if(remainder > 0):
      int_dict[min_key] = int(int_dict[min_key] + remainder/abs(remainder))
    else:
      int_dict[max_key] = int(int_dict[max_key] + remainder/abs(remainder))
    remainder -= int(remainder/abs(remainder))

  for dict_key in int_dict.keys():
    int_dict[dict_key] = str(int_dict[dict_key])
    if(len(int_dict[dict_key]) == 3):
      int_dict[dict_key] = '0.' + int_dict[dict_key]
    elif(len(int_dict[dict_key]) == 2):
      int_dict[dict_key] = '0.0' + int_dict[dict_key]
    else:
      int_dict[dict_key] = '0.00' + int_dict[dict_key] 


  print(key)
  payload = {
    "dividendCashAction": "REINVEST",
    "endDate": "2019-08-24T14:15:22Z",
    "goal": 25000,
    "icon": "Home",
    "instrumentShares": int_dict
    }
  headers = {
    "Content-Type": "application/json",
    "Authorization": key
    }
  
  pie_URL = "https://live.trading212.com/api/v0/equity/pies/" + str(id)
  response = requests.post(pie_URL, json=payload, headers=headers)
  return response

if __name__ == '__main__':
    app.run(debug=True)