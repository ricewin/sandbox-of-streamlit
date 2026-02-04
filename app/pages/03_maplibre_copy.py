import streamlit as st
from maplibre.basemaps import Carto
from maplibre.controls import Marker, NavigationControl
from maplibre.layer import Layer, LayerType
from maplibre.map import Map, MapOptions
from maplibre.sources import GeoJSONSource
from maplibre.streamlit import st_maplibre

st.title("MapLibre マップ表示サンプル")

# マップオプション
map_options = MapOptions(
    style=Carto.POSITRON,  # ベースマップスタイル
    center=(139.767, 35.681),  # 東京駅周辺の座標
    zoom=12,
    pitch=0,
)  # type: ignore

# マップを作成
m = Map(map_options)

# ナビゲーションコントロールを追加
m.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

# マーカーを追加
marker = Marker(lng_lat=(139.767, 35.681))
m.add_marker(marker)

# GeoJSONレイヤーを追加（シンプルなポイントの例）
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [139.767, 35.681]},
            "properties": {"name": "東京駅"},
        }
    ],
}

geojson_source = GeoJSONSource(data=geojson_data)  # pyright: ignore[reportCallIssue]

# 円レイヤーを追加
circle_layer = Layer(
    type=LayerType.CIRCLE,
    source=geojson_source,
    paint={
        "circle-radius": 10,
        "circle-color": "#007cbf",
        "circle-stroke-width": 2,
        "circle-stroke-color": "#ffffff",
    },
)  # pyright: ignore[reportCallIssue]

m.add_layer(circle_layer)

# Streamlitでマップを表示
st_maplibre(m)

st.write(
    "これはMapLibreを使ってStreamlitでマップを表示する基本的なサンプルです。マーカーとGeoJSONレイヤーが含まれています。"
)
