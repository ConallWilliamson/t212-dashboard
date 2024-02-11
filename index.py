import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([
    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.Col(dbc.NavbarBrand("T212 Dashboard")),
            dbc.NavLink("Settings", href="/settings"),
            # You can add more navigation links here if needed
        ],
        fluid=True),
        color="primary",
        dark=True
    ),
    dcc.Store(id='user-info', storage_type='session'),  # Store user info in session
    dcc.Store(id='is-logged-in', storage_type='session', data=False),  # Store to track login status in session
    dash.page_container
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
