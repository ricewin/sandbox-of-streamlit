"""
Shapefile Visualization with PyDeck

This page demonstrates how to visualize shapefiles using pydeck's GeoJsonLayer.
It supports both Shapefile (.shp) and GeoJSON (.geojson) formats.
"""

import geopandas as gpd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="Shapefile Visualization", page_icon="🗾", layout="wide")

# Constants
MAX_TOOLTIP_PROPERTIES = 5  # Maximum number of properties to show in tooltip


def load_shapefile_from_upload(uploaded_files):
    """
    Load shapefile from uploaded files (.shp, .shx, .dbf, .prj)

    Args:
        uploaded_files: Dictionary of uploaded files with extensions as keys

    Returns:
        GeoDataFrame containing the shapefile data
    """
    try:
        # Shapefileは複数のファイルで構成されているため、一時的に保存
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Upload files to temporary directory
            base_name = None
            for ext, file in uploaded_files.items():
                if ext == "shp":
                    base_name = file.name.replace(".shp", "")
                file_path = os.path.join(tmpdir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())

            # Ensure that a .shp file was provided
            if base_name is None:
                st.error("Uploaded shapefile set must include a .shp file.")
                return None

            # Read shapefile
            shp_path = os.path.join(tmpdir, f"{base_name}.shp")
            gdf = gpd.read_file(shp_path)

            # Ensure CRS is WGS84 (EPSG:4326) for web mapping
            if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            return gdf
    except Exception as e:
        st.error(f"Error loading shapefile: {str(e)}")
        return None


def load_geojson_from_upload(uploaded_file):
    """
    Load GeoJSON from uploaded file

    Args:
        uploaded_file: Uploaded GeoJSON file

    Returns:
        GeoDataFrame containing the GeoJSON data
    """
    try:
        gdf = gpd.read_file(uploaded_file)

        # Ensure CRS is WGS84 (EPSG:4326)
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON: {str(e)}")
        return None


@st.cache_data
def load_sample_data():
    """
    Load sample data from a public GeoJSON source

    Returns:
        GeoDataFrame containing sample data
    """
    # Use Natural Earth low-res countries data
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    try:
        gdf = gpd.read_file(url)
        return gdf
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        return None


def geodataframe_to_geojson(gdf):
    """
    Convert GeoDataFrame to GeoJSON format for pydeck

    Args:
        gdf: GeoDataFrame

    Returns:
        GeoJSON dictionary
    """
    return gdf.__geo_interface__


def get_bounds(gdf):
    """
    Get the bounding box of a GeoDataFrame

    Args:
        gdf: GeoDataFrame

    Returns:
        tuple: (min_lon, min_lat, max_lon, max_lat)
    """
    bounds = gdf.total_bounds
    return bounds[0], bounds[1], bounds[2], bounds[3]


def get_center_and_zoom(gdf):
    """
    Calculate center point and appropriate zoom level for the data

    Args:
        gdf: GeoDataFrame

    Returns:
        tuple: (latitude, longitude, zoom)
    """
    min_lon, min_lat, max_lon, max_lat = get_bounds(gdf)

    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    # Calculate zoom level based on bounds
    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon
    max_diff = max(lat_diff, lon_diff)

    # Simple zoom level calculation
    if max_diff > 100:
        zoom = 2
    elif max_diff > 50:
        zoom = 3
    elif max_diff > 20:
        zoom = 4
    elif max_diff > 10:
        zoom = 5
    elif max_diff > 5:
        zoom = 6
    elif max_diff > 1:
        zoom = 8
    else:
        zoom = 10

    return center_lat, center_lon, zoom


def create_pydeck_map(gdf, fill_color=None, line_color=None, opacity=0.5):
    """
    Create a pydeck map from GeoDataFrame

    Args:
        gdf: GeoDataFrame to visualize
        fill_color: RGB color for polygon fill
        line_color: RGB color for lines
        opacity: Opacity of the fill (0-1)

    Returns:
        pydeck.Deck object
    """
    if fill_color is None:
        fill_color = [255, 235, 215]
    if line_color is None:
        line_color = [255, 250, 205]
    # Convert to GeoJSON
    geojson_data = geodataframe_to_geojson(gdf)

    # Get center and zoom
    center_lat, center_lon, zoom = get_center_and_zoom(gdf)

    # Create view state
    view_state = pdk.ViewState(
        latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=0, bearing=0
    )

    # Create GeoJsonLayer
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        opacity=opacity,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        get_fill_color=fill_color,
        get_line_color=line_color,
        get_line_width=20,
        pickable=True,
    )

    # Create tooltip - show all properties (limited to MAX_TOOLTIP_PROPERTIES)
    tooltip = {
        "html": "<b>Properties:</b><br/>"
        + "<br/>".join(
            [f"{{{key}}}" for key in gdf.columns if key != "geometry"][
                :MAX_TOOLTIP_PROPERTIES
            ]
        ),
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "12px",
            "padding": "10px",
        },
    }

    # Create deck
    deck = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        tooltip=tooltip,  # pyright: ignore[reportArgumentType]
        map_style="light",
    )

    return deck


# Main UI
st.title("🗾 Shapefile Visualization with PyDeck")
st.markdown("""
This application demonstrates how to visualize geographic data using PyDeck's GeoJsonLayer.

**Supported formats:**
- **Shapefile** (.shp + .shx + .dbf + .prj) - Upload all required files together
- **GeoJSON** (.geojson or .json) - Upload a single file

**Note:** Shapefiles are automatically converted to GeoJSON format for visualization.
""")

# Sidebar for data source selection
st.sidebar.header("Data Source")
data_source = st.sidebar.radio(
    "Choose data source:", ["Sample Data", "Upload Shapefile", "Upload GeoJSON"]
)

gdf = None

if data_source == "Sample Data":
    st.sidebar.info("Using Natural Earth Countries sample data")
    with st.spinner("Loading sample data..."):
        gdf = load_sample_data()
        if gdf is not None:
            st.sidebar.success(f"Loaded {len(gdf)} features")

elif data_source == "Upload Shapefile":
    st.sidebar.markdown("""
    **Required files:**
    - .shp (required)
    - .shx (required)
    - .dbf (required)
    - .prj (optional but recommended)
    """)

    uploaded_files = {}

    # File uploaders for each shapefile component
    shp_file = st.sidebar.file_uploader("Upload .shp file", type=["shp"], key="shp")
    shx_file = st.sidebar.file_uploader("Upload .shx file", type=["shx"], key="shx")
    dbf_file = st.sidebar.file_uploader("Upload .dbf file", type=["dbf"], key="dbf")
    prj_file = st.sidebar.file_uploader(
        "Upload .prj file (optional)", type=["prj"], key="prj"
    )

    if shp_file and shx_file and dbf_file:
        uploaded_files["shp"] = shp_file
        uploaded_files["shx"] = shx_file
        uploaded_files["dbf"] = dbf_file
        if prj_file:
            uploaded_files["prj"] = prj_file

        with st.spinner("Loading shapefile..."):
            gdf = load_shapefile_from_upload(uploaded_files)
            if gdf is not None:
                st.sidebar.success(f"Loaded {len(gdf)} features")

elif data_source == "Upload GeoJSON":
    geojson_file = st.sidebar.file_uploader(
        "Upload GeoJSON file", type=["geojson", "json"]
    )

    if geojson_file:
        with st.spinner("Loading GeoJSON..."):
            gdf = load_geojson_from_upload(geojson_file)
            if gdf is not None:
                st.sidebar.success(f"Loaded {len(gdf)} features")

# Display data and map if loaded
if gdf is not None:
    # Display basic information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of Features", len(gdf))
    with col2:
        if len(gdf) > 0 and not gdf.geometry.empty:
            try:
                geometry_type_metric = gdf.geometry.type.value_counts().index[0]
            except IndexError, KeyError:
                geometry_type_metric = "N/A"
        else:
            geometry_type_metric = "N/A"
        st.metric("Geometry Type", geometry_type_metric)
    with col3:
        if gdf.crs:
            epsg = gdf.crs.to_epsg()
            crs_display = f"EPSG:{epsg}" if epsg else "Custom CRS"
            st.metric("CRS", crs_display)
        else:
            st.metric("CRS", "Unknown")

    # Styling options
    st.sidebar.header("Styling Options")

    fill_color = st.sidebar.color_picker("Fill Color", "#FFE4B5")
    line_color = st.sidebar.color_picker("Line Color", "#FFFACD")
    opacity = st.sidebar.slider("Opacity", 0.0, 1.0, 0.5, 0.1)

    # Convert hex to RGB
    fill_rgb = [int(fill_color[i : i + 2], 16) for i in (1, 3, 5)]
    line_rgb = [int(line_color[i : i + 2], 16) for i in (1, 3, 5)]

    # Create and display map
    st.subheader("Map Visualization")
    deck = create_pydeck_map(gdf, fill_rgb, line_rgb, opacity)
    st.pydeck_chart(deck, height=600)

    # Display attribute table
    with st.expander("View Attribute Table"):
        st.dataframe(gdf.drop(columns=["geometry"]))

    # Display GeoJSON
    with st.expander("View GeoJSON Format"):
        st.json(geodataframe_to_geojson(gdf), expanded=False)

    # Technical details
    with st.expander("Technical Details"):
        st.markdown("""
        ### Implementation Details

        **Shapefile Handling:**
        1. Shapefiles are uploaded with all required components (.shp, .shx, .dbf, .prj)
        2. Files are temporarily saved to disk (shapefiles require file system access)
        3. GeoPandas reads the shapefile
        4. Data is reprojected to WGS84 (EPSG:4326) if necessary
        5. GeoDataFrame is converted to GeoJSON format

        **GeoJSON Handling:**
        1. GeoJSON files are read directly by GeoPandas
        2. Data is reprojected to WGS84 (EPSG:4326) if necessary
        3. GeoDataFrame is ready for visualization

        **PyDeck Visualization:**
        - Uses `GeoJsonLayer` which supports both Polygon and MultiPolygon geometries
        - Automatically calculates appropriate zoom level and center point
        - Features are pickable with tooltips showing attributes

        **Libraries Used:**
        - `geopandas`: For reading and processing spatial data
        - `pydeck`: For creating interactive maps
        - `streamlit`: For the web interface
        """)
else:
    st.info("👈 Please select a data source from the sidebar to begin.")

st.markdown("---")
st.markdown("""
**Tips:**
- For large shapefiles, consider simplifying the geometry first
- Ensure all shapefile components have the same basename
- GeoJSON is often easier to work with for web applications
- The visualization automatically handles coordinate system conversion
""")
