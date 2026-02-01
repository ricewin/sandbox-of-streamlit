"""
Example: Shapefile to PyDeck Visualization

このスクリプトは、シェープファイルをPyDeckで可視化する基本的な方法を示します。
This script demonstrates the basic approach to visualizing shapefiles with PyDeck.
"""

import geopandas as gpd
import pydeck as pdk

# Default styling constants
DEFAULT_FILL_COLOR = [255, 235, 215]  # Light orange
DEFAULT_LINE_COLOR = [255, 250, 205]  # Light yellow


def shapefile_to_pydeck(shapefile_path, output_html="map.html"):
    """
    シェープファイルをPyDeckで可視化する基本的な関数
    Basic function to visualize a shapefile with PyDeck
    
    Args:
        shapefile_path (str): Path to the .shp file
        output_html (str): Output HTML file path
    
    Returns:
        pydeck.Deck: PyDeck map object
    """
    
    # 1. シェープファイルを読み込み / Load shapefile
    print(f"Loading shapefile: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    print(f"Loaded {len(gdf)} features")
    print(f"Geometry types: {gdf.geometry.type.value_counts().to_dict()}")
    print(f"CRS: {gdf.crs}")
    
    # 2. WGS84 (EPSG:4326) に変換 / Convert to WGS84
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        print("Converting to WGS84...")
        gdf = gdf.to_crs(epsg=4326)
    
    # 3. GeoJSON 形式に変換 / Convert to GeoJSON format
    print("Converting to GeoJSON...")
    geojson_data = gdf.__geo_interface__
    
    # 4. 中心点とズームレベルを計算 / Calculate center and zoom
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    
    # Simple zoom calculation
    lat_diff = bounds[3] - bounds[1]
    lon_diff = bounds[2] - bounds[0]
    max_diff = max(lat_diff, lon_diff)
    
    if max_diff > 100:
        zoom = 2
    elif max_diff > 50:
        zoom = 3
    elif max_diff > 10:
        zoom = 4
    else:
        zoom = 6
    
    print(f"Center: ({center_lat:.4f}, {center_lon:.4f}), Zoom: {zoom}")
    
    # 5. PyDeck レイヤーを作成 / Create PyDeck layer
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        opacity=0.5,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        get_fill_color=DEFAULT_FILL_COLOR,
        get_line_color=DEFAULT_LINE_COLOR,
        get_line_width=20,
        pickable=True,
    )
    
    # 6. ビューステートを設定 / Set view state
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0,
        bearing=0
    )
    
    # 7. Deck を作成 / Create deck
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light"
    )
    
    # 8. HTML ファイルとして保存 / Save as HTML
    print(f"Saving to {output_html}...")
    deck.to_html(output_html)
    print(f"✓ Map saved to {output_html}")
    
    return deck


def geojson_to_pydeck(geojson_path, output_html="map.html"):
    """
    GeoJSONファイルをPyDeckで可視化する基本的な関数
    Basic function to visualize a GeoJSON file with PyDeck
    
    Args:
        geojson_path (str): Path to the .geojson or .json file
        output_html (str): Output HTML file path
    
    Returns:
        pydeck.Deck: PyDeck map object
    """
    
    # GeoJSON も GeoPandas で読み込み、shapefileと同じ処理を使用
    # Load GeoJSON with GeoPandas and use the same processing as shapefile
    return shapefile_to_pydeck(geojson_path, output_html)


if __name__ == "__main__":
    """
    使用例 / Example Usage
    
    コマンドラインから実行:
    Run from command line:
    
    python examples/shapefile_example.py
    """
    
    # サンプルデータの URL (Natural Earth Countries)
    # Sample data URL (Natural Earth Countries)
    sample_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    
    print("=" * 60)
    print("Shapefile to PyDeck Example")
    print("=" * 60)
    print()
    
    try:
        # オンラインの GeoJSON を読み込んで可視化
        # Load and visualize online GeoJSON
        deck = shapefile_to_pydeck(sample_url, "world_countries.html")
        
        print()
        print("=" * 60)
        print("✓ Success!")
        print("Open 'world_countries.html' in your browser to view the map.")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print()
        print("To use with your own shapefile:")
        print("  deck = shapefile_to_pydeck('path/to/your/file.shp')")
        print()
        print("To use with GeoJSON:")
        print("  deck = shapefile_to_pydeck('path/to/your/file.geojson')")
