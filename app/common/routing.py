import streamlit as st
from streamlit.navigation.page import StreamlitPage


def navigation() -> None:
    pages: dict[str, list[StreamlitPage]] = {
        "Contents": [
            st.Page("pages/01_game.py", title="Simple Game"),
            st.Page("pages/02_pydeck.py", title="Plot Japan Map"),
            st.Page("pages/03_maplibre.py", title="Maplibre Map"),
            st.Page("pages/04_shapefile_pydeck.py", title="Shapefile Visualization"),
            st.Page("pages/05_isochrone_api.py", title="Mapbox Isochrone API"),
        ],
        # "Resources": [
        #     st.Page("pages/learn.py", title="Learn about me"),
        # ],
    }

    pg: StreamlitPage = st.navigation(pages)
    pg.run()


def page_config() -> None:
    TITLE = "Streamlit Playground"

    st.set_page_config(
        page_title=TITLE,
        page_icon="🏗️",
        layout="wide",
    )

    with st.sidebar:
        st.markdown(":satellite: testing...")
        st.caption(f"*Streamlit Ver.{st.__version__}*")
