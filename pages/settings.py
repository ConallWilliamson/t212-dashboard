import dash
from dash import dcc, html

dash.register_page(__name__)


layout = html.Div([
    html.H1("Profile Page"),
    # Add profile content here
])