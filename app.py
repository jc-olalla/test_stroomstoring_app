import dash
from dash import dcc, html
import plotly.graph_objects as go
from zip_codes_and_map import fig  # Import your Plotly figure

# Initialize Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    dcc.Graph(
        id="map-graph",
        figure=fig,
        style={
            "height": "80vh",  # Takes most of the screen height
            "width": "100%",  # Full width for any screen
        }
    ),

    html.Script("""
    function adjustToolbar() {
        let graph = document.getElementById('map-graph');
        let config = graph.layout.config || {};

        if (window.innerWidth < 768) {
            config.displayModeBar = false;  // Hide toolbar on mobile
        } else {
            config.displayModeBar = true;   // Show toolbar on laptop
        }

        graph.layout.config = config;
        Plotly.react(graph, graph.data, graph.layout);
    }

    window.addEventListener('resize', adjustToolbar);
    window.onload = adjustToolbar;
    """, type="text/javascript")
])

# Expose the server
server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)
