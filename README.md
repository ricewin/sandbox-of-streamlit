# Streamlit Sandbox Gen.2

## Playground

Getting started: [30 Days of Streamlit.](https://30days.streamlit.app/)

### Highlights

- 🚀 Using uv as the package management tool.
- ⚡️ Using ruff as the linter and code formatter.
- 🗾 **NEW**: Shapefile visualization with PyDeck - [Documentation](docs/SHAPEFILE_VISUALIZATION.md)

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
   streamlit run app/main.py
   ```

## Features

### Shapefile Visualization (NEW)

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
