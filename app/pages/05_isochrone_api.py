import pydeck as pdk
import requests
import streamlit as st

st.title("🔮 Mapbox Isochrone Demo")

MAPBOX_TOKEN = st.secrets.mapbox.token

# 入力 UI
lat = st.number_input("Latitude", value=35.681236)
lon = st.number_input("Longitude", value=139.767125)
routing_profile = st.selectbox(
    "Routing Profile",
    options=["driving", "driving-traffic", "walking", "cycling"],
    index=0,
)
minutes = st.slider("Travel time (minutes)", 1, 60, 10)

# API 呼び出し
url = (
    f"https://api.mapbox.com/isochrone/v1/mapbox/{routing_profile}/"
    f"{lon},{lat}?contours_minutes={minutes}&polygons=true&access_token={MAPBOX_TOKEN}"
)

res = requests.get(url)
geojson = res.json()

# pydeck レイヤー
layer = pdk.Layer(
    "GeoJsonLayer",
    geojson,
    opacity=0.4,
    stroked=True,
    filled=True,
    get_fill_color=[255, 0, 0, 80],
    get_line_color=[255, 0, 0, 200],
)

view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=12)

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        api_keys={"mapbox": MAPBOX_TOKEN},
        map_provider="mapbox",
    )
)
