# Copilot instructions for sandbox-of-streamlit

## Big picture

- Streamlit app entrypoint is [app/main.py](app/main.py), which only calls `page_config()` and `navigation()` from [app/common/routing.py](app/common/routing.py).
- Pages live under [app/pages/](app/pages/) and are wired via `st.navigation` in [app/common/routing.py](app/common/routing.py). Add new pages by creating a file in app/pages and registering it in `pages`.
- Shared helpers live in [app/common/](app/common/): `require_mapbox_token()` in [app/common/secrets.py](app/common/secrets.py) enforces Mapbox secrets; `StepByStep` in [app/common/step_by_step.py](app/common/step_by_step.py) implements multi-step UI with `st.fragment` + session state.

## Data flows and integrations

- Mapbox Isochrone demo (API call + PyDeck) is in [app/pages/05_isochrone_api.py](app/pages/05_isochrone_api.py); it reads `st.secrets.mapbox.token` and caches API calls via `@st.cache_data`.
- HERE Traffic demo (HERE Flow API + MapLibre) is in [app/pages/06_here_traffic.py](app/pages/06_here_traffic.py); it uses `@st.cache_data(ttl=300)` and has a no-key demo mode with sample GeoJSON.
- Shapefile visualization uses GeoPandas + PyDeck in [app/pages/04_shapefile_pydeck.py](app/pages/04_shapefile_pydeck.py); uploads require .shp/.shx/.dbf (and optional .prj) saved to a temp dir before reading.

## Developer workflows

- Install deps with `uv sync` (see [README.md](README.md) and [pyproject.toml](pyproject.toml)).
- Run locally with `./run_app.sh`, which executes `uv run streamlit run app/main.py` with CORS/XSRF disabled (see [run_app.sh](run_app.sh)).
- When Python files change, run `ruff check` and `ruff format` (ruff is listed in [pyproject.toml](pyproject.toml)).
- When Markdown files change, consider running markdownlint locally if you have it installed (note: this repo does not include markdownlint config or CI).

## Project-specific conventions

- Use Streamlit’s caching (`@st.cache_data`) for external API fetches (see [app/pages/05_isochrone_api.py](app/pages/05_isochrone_api.py), [app/pages/06_here_traffic.py](app/pages/06_here_traffic.py)).
- UI state is managed with `st.session_state` and, for multi-step flows, `StepByStep` (`@st.fragment`) in [app/common/step_by_step.py](app/common/step_by_step.py).
- Map rendering alternates between PyDeck (`st.pydeck_chart`) and MapLibre (`st_maplibre`) depending on the demo.

## Secrets/config

- Mapbox token must be set in .streamlit/secrets.toml under [mapbox] (enforced by `require_mapbox_token()` in [app/common/secrets.py](app/common/secrets.py)).
- HERE API key is user-entered via sidebar and stored in session state (see [app/pages/06_here_traffic.py](app/pages/06_here_traffic.py)).
