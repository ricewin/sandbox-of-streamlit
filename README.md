# Streamlit Sandbox Gen.2

## Playground

Getting started: [30 Days of Streamlit.](https://30days.streamlit.app/)

### Highlights

- 🚀 Using uv as the package management tool.
- ⚡️ Using ruff as the linter and code formatter.
- 🔮 **NEW**: Mapbox Isochrone API demo with PyDeck - [Documentation](docs/MAPBOX_ISOCHRONE.md)
- 🗾 Shapefile visualization with PyDeck - [Documentation](docs/SHAPEFILE_VISUALIZATION.md)

## Getting Started

### Prerequisites

- Python 3.14 or higher
- uv package manager

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ricewin/sandbox-of-streamlit.git
   cd sandbox-of-streamlit
   ```

2. Install dependencies using uv:

   ```bash
   uv sync
   ```

3. Run the Streamlit app:

   ```bash
   ./run_app.sh
   ```

   Or manually:

   ```bash
   uv run streamlit run app/main.py
   ```

## Features

### Mapbox Isochrone API Demo (NEW)

Interactive visualization of travel time polygons using the Mapbox Isochrone API. Shows areas reachable within specified time intervals from any location.

**Page**: `app/pages/05_isochrone_api.py`

**Key Features**:

- 🗺️ Interactive Mapbox map visualization
- ⏱️ Adjustable travel time (1-60 minutes)
- 🚗 Multiple routing profiles (driving, walking, cycling, driving-traffic)
- 📍 Custom location coordinates
- 💾 API response caching for performance
- 🔒 Secure token handling with URL restrictions

See [MAPBOX_ISOCHRONE.md](docs/MAPBOX_ISOCHRONE.md) for detailed documentation and security best practices.

### Shapefile Visualization

Interactive visualization of geographic data using PyDeck's GeoJsonLayer. Supports both Shapefile and GeoJSON formats with automatic coordinate system conversion.

**Page**: `app/pages/04_shapefile_pydeck.py`

**Key Features**:

- ✅ Upload and visualize Shapefiles (.shp + .shx + .dbf + .prj)
- ✅ Upload and visualize GeoJSON files (.geojson, .json)
- ✅ Sample data demo with Natural Earth Countries
- ✅ Customizable styling (colors, opacity)
- ✅ Automatic WGS84 coordinate conversion
- ✅ Interactive tooltips with attribute information

See [SHAPEFILE_VISUALIZATION.md](docs/SHAPEFILE_VISUALIZATION.md) for detailed documentation.
