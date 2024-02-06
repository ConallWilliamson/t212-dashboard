import dash
from dash import Dash, html, dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

app.layout = html.Div([
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)