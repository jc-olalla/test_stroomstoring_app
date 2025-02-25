import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load GeoDataFrames and convert to WGS 84 (EPSG:4326)
gdf_0930 = gpd.read_file("data/stroomstoring_2025-03-09 09:30.gpkg").to_crs(4326)
gdf_1030 = gpd.read_file("data/stroomstoring_2025-03-09 10:30.gpkg").to_crs(4326)
gdf_1130 = gpd.read_file("data/stroomstoring_2025-03-09 11:30.gpkg").to_crs(4326)
gdf_1230 = gpd.read_file("data/stroomstoring_2025-03-09 12:30.gpkg").to_crs(4326)

# Load point dataset (events)
evenements = gpd.read_file("data/evenementen.gpkg").to_crs(4326)

# Add a 'timestamp' column to each GeoDataFrame
gdf_0930["timestamp"] = "09:30"
gdf_1030["timestamp"] = "10:30"
gdf_1130["timestamp"] = "11:30"
gdf_1230["timestamp"] = "12:30"

# Combine all GeoDataFrames into one
gdf_combined = pd.concat([gdf_0930, gdf_1030, gdf_1130, gdf_1230], ignore_index=True)

# Compute fixed bounding box
min_lon, min_lat, max_lon, max_lat = gdf_combined.total_bounds
center_lat = (max_lat + min_lat) / 2
center_lon = (max_lon + min_lon) / 2

# Compute total affected inhabitants for each timestamp
total_affected = gdf_combined.groupby("timestamp")["aantalInwoners"].sum().to_dict()

# Create Frames for Animation
frames = []
timestamps = gdf_combined["timestamp"].unique()
timestamps.sort()

for timestamp in timestamps:
    gdf_frame = gdf_combined[gdf_combined["timestamp"] == timestamp]

    frames.append(go.Frame(
        data=[
            go.Choroplethmapbox(
                geojson=gdf_frame.__geo_interface__,
                locations=gdf_frame.index,
                z=gdf_frame["aantalInwoners"],
                colorscale="turbo",
                zmin=0,
                zmax=10000,  # gdf_combined["aantalInwoners"].max(),
                featureidkey="id",
                marker_opacity=0.7,
                marker_line_width=0
            )
        ],
        name=timestamp,
        layout=go.Layout(
            annotations=[{
                "text": f"<b>Getroffen door Stroomstoring (09-03-2025):<br>{total_affected[timestamp]:,}</b>",
                "x": 0.5, "y": 0.99,  # Position inside map
                "xref": "paper", "yref": "paper",
                "showarrow": False,
                "font": {"size": 30, "color": "White"},
                "bgcolor": "rgba(0, 0, 0, 0.7)",  # Dark background for contrast
                "borderpad": 10
            }]
        )
    ))

# Add the first annotation (for initial timestamp)
initial_affected = total_affected[timestamps[0]]

# Create Figure with Mapbox Tile Background
fig = go.Figure(
    data=[
        go.Choroplethmapbox(
            geojson=gdf_combined.__geo_interface__,
            locations=gdf_combined.index,
            z=gdf_combined["aantalInwoners"],
            colorscale="turbo",
            zmin=0,
            zmax=10000,
            featureidkey="id",
            marker_opacity=0.7,
            marker_line_width=0
        ),
        # Overlay Static Points
        go.Scattermapbox(
            lat=evenements.geometry.y,
            lon=evenements.geometry.x,
            mode="markers",
            marker=dict(size=10, color="red"),
            name="Event Locations"
        )
    ],
    frames=frames
)

# Set Mapbox Style and Viewport
fig.update_layout(
    mapbox_style="open-street-map",  # Tile-based map
    mapbox_center={"lat": center_lat, "lon": center_lon},
    mapbox_zoom=11,

    # **Make map full-screen**
    height=800,  # Adjust for full-screen look
    margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Remove all margins

    # **Fix Play/Pause Button Placement**
    updatemenus=[{
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 10},  # Adjusted padding
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0.05,  # Lowered so it's visible
        "yanchor": "bottom"  # Changed anchor from "top" to "bottom"
    }]
)


# Hover info
fig.update_traces(
    selector=dict(type="choroplethmapbox"),
    hoverinfo="text",  # Use text for hover labels
    hovertemplate="<b>Postcode:</b> %{customdata[0]}<br>"
                  "<b>Aantal Inwoners:</b> %{z}<extra></extra>",  # Removes extra box
    customdata=gdf_combined[["postcode", "aantalInwoners"]].values  # Passes additional data
)


# Color bar
fig.update_traces(
    selector=dict(type="choroplethmapbox"),
    colorscale="turbo",  # Continuous gradient color scale
    colorbar=dict(
        orientation="h",  # Horizontal colorbar
        x=0.9,  # Center horizontally
        y=0.85,  # Position below the map
        thickness=10,  # Slimmer colorbar
        len=0.2,  # Adjust width
        bgcolor="rgba(255,255,255,0.6)",  # Light background for contrast
        title="Aantal Inwoners per postcode",  # Label for colorbar
        title_side="top"  # Puts title above the colorbar
    ),
    zmin=0,
    zmax=10000
)

# Create slider steps for each timestamp
timestamps = sorted(gdf_combined["timestamp"].unique())  # Ensure correct order
steps = [
    {
        "args": [
            [ts],  # Frame to show
            {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}
        ],
        "label": ts,  # Label displayed in slider
        "method": "animate"
    }
    for ts in timestamps
]

# Add slider to layout
# Add slider inside the map with reduced width
fig.update_layout(
    sliders=[{
        "active": 0,  # Start at first timestamp
        "steps": steps,  # Add clickable timestamps
        "yanchor": "bottom",  # Move inside the map
        "xanchor": "center",
        "currentvalue": {
            "font": {"size": 36, "color": "black"},
            "prefix": "Current Time: ",
            "visible": True
        },
        "transition": {"duration": 0},  # Instant update on click
        "pad": {"b": 10, "t": 10},  # Reduce padding
        "len": 0.7,  # Reduce width
        "x": 0.5,  # Center horizontally
        "y": 0.05, # Position inside map
        "bgcolor": "rgba(0, 0, 0, 0.7)",  # Dark background for visibility
        "bordercolor": "black",  # White border for contrast
        "borderwidth": 2,  # Thicker border for emphasis
        "font": {"size": 14, "color": "black"}  # Increase label size
    }]
)


# Add logo
fig.add_layout_image(
    source="https://www.zhzveilig.nl/themes/zhzveilig_corporate_theme/logo.svg",
    x=0.13,
    y=0.84,
    xanchor="right",
    yanchor="bottom",
    sizex=0.15,
    sizey=0.15,
)

# Add hover to markers
# Add hover to markers
fig.update_traces(
    selector=dict(type="scattermapbox"),
    hoverinfo="text",
    hovertemplate="<b>Referentienummer:</b> %{customdata[0]}<br>"
                  "<b>Datum:</b> %{customdata[1]}<br>"  # Fixed missing line break
                  "<b>Event naam:</b> %{customdata[2]}<br>"  # Fixed missing line break
                  "<b>Lokatie:</b> %{customdata[3]}<extra></extra>",  # Fixed hover format
    customdata=evenements[["Referentienummer", "Datum", "Naam", "Lokatie"]].values  # Ensure all fields are passed
)

fig.show()

# TODO:
# host app online
# markers legend
# clickable layers: evenementen, hospitals, supermarkets
# Make a story: presentation
# Sent web link to them
