import pydeck as pdk
import requests
import streamlit as st
from common.step_by_step import StepByStep


def get_rough_center(geojson):
    geom = geojson["features"][0]["geometry"]

    if geom["type"] == "Polygon":
        coords = geom["coordinates"][0]
    elif geom["type"] == "MultiPolygon":
        coords = geom["coordinates"][0][0]  # 最初のポリゴンの外周
    else:
        raise ValueError("対応していないジオメトリタイプです")

    lon, lat = zip(*coords)
    return sum(lat) / len(lat), sum(lon) / len(lon)


@st.cache_data
def get_geojson_center(geojson):
    # 全ての座標を走査して最小・最大の緯度経度を探す
    def extract_coords(geometry):
        coords = []
        if geometry["type"] == "Polygon":
            coords.extend(geometry["coordinates"][0])
        elif geometry["type"] == "MultiPolygon":
            for polygon in geometry["coordinates"]:
                coords.extend(polygon[0])
        return coords

    all_coords = []
    for feature in geojson["features"]:
        coords = extract_coords(feature["geometry"])
        all_coords.extend(coords)

    lon = [pt[0] for pt in all_coords]
    lat = [pt[1] for pt in all_coords]

    center_lon = (min(lon) + max(lon)) / 2
    center_lat = (min(lat) + max(lat)) / 2

    return center_lat, center_lon


@st.cache_data
def get_geojson_bbox(geojson):
    def extract_coords(geometry):
        coords = []
        if geometry["type"] == "Polygon":
            coords.extend(geometry["coordinates"][0])
        elif geometry["type"] == "MultiPolygon":
            for polygon in geometry["coordinates"]:
                coords.extend(polygon[0])
        return coords

    all_coords = []
    for feature in geojson["features"]:
        coords = extract_coords(feature["geometry"])
        all_coords.extend(coords)

    lon = [pt[0] for pt in all_coords]
    lat = [pt[1] for pt in all_coords]

    return [min(lon), min(lat), max(lon), max(lat)]


@st.fragment
def fetch_data(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


@st.fragment
def make_map(DATA, zoom: int = 4, level: int = 1):
    pcode = f"N03_00{level}"

    lat, lon = get_geojson_center(DATA)
    # lat, lon = get_rough_center(DATA)

    INITIAL_VIEW_STATE = pdk.ViewState(
        latitude=lat, longitude=lon, zoom=zoom, max_zoom=16, pitch=0, bearing=0
    )

    geojson = pdk.Layer(
        "GeoJsonLayer",
        DATA,
        id="geojson",
        pickable=True,
        opacity=0.1,
        get_fill_color="[255, 235, 215]",
        get_line_color=[255, 250, 205],
        get_line_width=100,
    )

    tooltip = {
        "html": f"<b>{{{pcode}}}</b>",
        "style": {
            "background-color": "teal",
            "color": "aliceblue",
            "font-family": "Noto Sans JP, sans-serif",
            "border-radius": "50% 20% / 10% 40%",
        },
    }

    r = pdk.Deck(
        map_style="dark_no_labels",
        layers=[geojson],
        initial_view_state=INITIAL_VIEW_STATE,
        tooltip=tooltip,  # type: ignore
    )

    choose_map(r)


@st.fragment
def choose_map(r):
    event = st.pydeck_chart(r, height=800, on_select="rerun")

    with st.expander("*Detailed information on the selected region.*"):
        if obj := event.selection.objects:  # type: ignore
            st.caption(obj.geojson[0]["properties"]["N03_001"])
            st.caption(obj.geojson[0]["properties"]["N03_007"])
            st.write(obj)

            ss.indices = event.selection.indices["geojson"][0]  # type: ignore
            ss.event = obj


@st.fragment
def step1():
    # 都道府県データを取得
    DATA = fetch_data(
        "https://raw.githubusercontent.com/ricewin/simplify-japan-geojson/refs/heads/main/GeoJson/prefecture.json"
    )

    make_map(DATA)


@st.fragment
def step2():
    # 都道府県選択イベントを取得
    obj = ss.event

    if obj is None:
        step.buttons(ss.now, True)
        st.rerun()

    pref = obj.geojson[0]["properties"]["N03_001"]
    code = obj.geojson[0]["properties"]["N03_007"][:2]
    st.caption(f"{pref}")

    DATA = fetch_data(
        f"https://raw.githubusercontent.com/ricewin/simplify-japan-geojson/refs/heads/main/GeoJson/{code}.json"
    )

    make_map(DATA, zoom=8, level=4)


@st.fragment
def step3():
    st.info("Continue making...")
    obj = ss.event

    st.write(obj.geojson[0]["properties"])

    # bbox = get_geojson_bbox(obj.geojson[0])
    # print("BBOX:", bbox)


ss = st.session_state

if "event" not in ss:
    ss.event = None

# main
st.title("In progress")
st.caption("*To be continued...*")

step = StepByStep()

try:
    if ss.now == 0:
        st.subheader("*Step.1 : Select prefecture*")
        step1()

        st.caption("After selecting, click “Next”.")
    elif ss.now == 1:
        st.subheader("*Step.2 : Select city, town or village*")
        step2()

        st.caption("After selecting, click “Next”.")
    elif ss.now == 2:
        st.subheader("*Step.3*")
        step3()

    else:
        st.subheader("*Success*")
        st.success("All steps have been completed.")
finally:
    step.buttons(ss.now)
