from dash import Dash, Input, Output, dcc, html, State, callback
import dash_auth
import json
import requests

f_subs = open('subs.json')
subs = json.load(f_subs)

f_pies = open('pies.json')
pies = json.load(f_pies)
keys = pies.keys()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.H6("Please enter your API key here"),
    html.Div([
        "API Key : ",
        dcc.Input(id='input-on-submit', type='text')]),

    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='my-output'),

    html.Button('Fetch all Pies', id='fetch-all', n_clicks = 0),
    html.Div(id='available-pies'),

    dcc.Dropdown(list(keys),id = 'pie-dropdown'),
    html.Div(id='pie-selection')
])


@callback(
    Output('my-output', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value'),
    prevent_initial_call=True
)
def update_available_instruments(n_clicks, value):
    response = get_instruments(value)
    status_code = response.status_code
    if status_code != 200:
        return 'T212 responded with a status code of "{}".\n Ensure you have a valid API key and try again.'.format(status_code)
    else:
        return response.text

@callback(
    Output('available-pies', 'children'),
    Input('fetch-all','n_clicks'),
    State('input-on-submit', 'value'),
    prevent_initial_call=True
)
def update_available_pies(n_clicks, value):
    print(value)
    response = get_all_pies(value)
    status_code = response.status_code
    if status_code != 200:
        return 'T212 responded with a status code of "{}". Ensure you have a valid API key and try again.'.format(status_code)
    else:
        return response.text

@callback(
        Output('pie-selection', 'children'),
        [Input('pie-dropdown', 'value'),
        Input('input-on-submit', 'value')],
        prevent_initial_call=True
)    
def confirm_pie_selection(pie_dropdown, api_key):
    return 'you have selected "{}". This has a pie ID of "{}". You have an API key of "{}".'.format(pie_dropdown,pies[pie_dropdown],api_key)


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

if __name__ == '__main__':
    app.run(debug=True)