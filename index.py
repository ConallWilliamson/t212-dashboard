import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc



#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages = True)
app.layout = dbc.Container(html.Div([
    dash.page_container
]), fluid = True)

if __name__ == '__main__':
    app.run(debug=True)