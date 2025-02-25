import dash
from dash import dcc, html
import plotly.graph_objects as go
from zip_codes_and_map import fig  # Import the Plotly figure from your script

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    # html.H1("Stroomstoring Animatiekaart Gorinchem", style={'textAlign': 'center'}),
    dcc.Graph(figure=fig)  # Display the Plotly map
])

# Expose the server for Render
server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)

