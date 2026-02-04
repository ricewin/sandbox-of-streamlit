import pydeck as pdk
import requests
import streamlit as st

st.title("🔮 Mapbox Isochrone Demo")

if "mapbox_validated" not in st.session_state:
    from common.secrets import require_mapbox_token

    require_mapbox_token()
    st.session_state.mapbox_validated = True


@st.cache_data
def fetch_isochrone(lat, lon, routing_profile, minutes):
    """Fetch isochrone data from Mapbox API (with caching)"""
    base_url = (
        f"https://api.mapbox.com/isochrone/v1/mapbox/{routing_profile}/{lon},{lat}"
    )

    params = {
        "contours_minutes": minutes,
        "polygons": "true",
        "access_token": st.secrets.mapbox.token,
    }

    try:
        res = requests.get(base_url, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch isochrone data from Mapbox: {e}")
        # Return safe fallback value (empty GeoJSON)
        return {"type": "FeatureCollection", "features": []}


# Input UI
lat = st.number_input("Latitude", value=35.681236)
lon = st.number_input("Longitude", value=139.767125)
routing_profile = st.selectbox(
    "Routing Profile",
    options=["driving", "driving-traffic", "walking", "cycling"],
    index=0,
)
minutes = st.slider("Travel time (minutes)", 1, 60, 10)

# API call (with caching)
geojson = fetch_isochrone(lat, lon, routing_profile, minutes)

# PyDeck layer
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

# Note: Passing the Mapbox token via api_keys is the standard approach documented by Streamlit.
# See: https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart
# Mapbox tokens are designed for client-side use. For security, configure URL restrictions
# and appropriate scopes in your Mapbox account settings: https://account.mapbox.com/
st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        api_keys={"mapbox": st.secrets.mapbox.token},
        map_provider="mapbox",
    )
)
