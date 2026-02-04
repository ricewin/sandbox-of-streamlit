# Mapbox Isochrone API Demo

This demo showcases how to use the Mapbox Isochrone API with Streamlit and PyDeck to visualize travel time polygons.

## Overview

The Isochrone API returns polygons showing areas reachable within specified time intervals from a location using different modes of transportation (driving, walking, cycling).

**Page**: `app/pages/05_isochrone_api.py`

## Setup

### 1. Create a Mapbox Account

1. Sign up for a free account at [mapbox.com](https://mapbox.com/)
2. Navigate to your [account page](https://account.mapbox.com/)
3. Create a new access token or use your default public token

### 2. Configure Secrets

Add your Mapbox token to Streamlit secrets:

**`.streamlit/secrets.toml`**:
```toml
[mapbox]
token = "pk.your_mapbox_token_here"
```

### 3. Security Best Practices

**Mapbox tokens are designed for client-side use**, which is why passing them via pydeck's `api_keys` parameter is the standard approach documented by Streamlit. However, you should still follow these security best practices:

#### Token Restrictions

Configure URL restrictions in your [Mapbox account settings](https://account.mapbox.com/):

- **Development**: Restrict to `localhost` and your development domains
- **Production**: Restrict to your production domain(s) only
  
Example URL restrictions:
```
http://localhost:*
https://yourdomain.com/*
https://*.yourdomain.com/*
```

#### Token Scopes

Use tokens with minimal required scopes:

- ✅ For this demo, you only need: `styles:read`, `fonts:read`, and the Isochrone API scope
- ❌ Avoid using tokens with write permissions or sensitive data access

#### Token Types

- **Public tokens** (starting with `pk.`): Safe for client-side use with URL restrictions
- **Secret tokens** (starting with `sk.`): Never use in client-side code

## Features

- 🗺️ **Interactive Map Visualization**: View isochrone polygons on an interactive Mapbox map
- ⏱️ **Adjustable Travel Time**: Use slider to set travel time from 1-60 minutes
- 🚗 **Multiple Routing Profiles**: Choose from driving, driving-traffic, walking, or cycling
- 📍 **Custom Locations**: Set any latitude/longitude coordinates
- 💾 **Caching**: API responses are cached for better performance

## How It Works

1. **API Request**: The app sends a request to the Mapbox Isochrone API with:
   - Location coordinates (lat, lon)
   - Routing profile (driving, walking, cycling)
   - Travel time in minutes

2. **Data Processing**: The API returns a GeoJSON FeatureCollection containing polygon(s) representing reachable areas

3. **Visualization**: PyDeck renders the polygons on an interactive map using Mapbox as the base map provider

## Code Reference

The implementation follows [Streamlit's official documentation](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart) for using Mapbox with pydeck:

```python
st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        api_keys={"mapbox": MAPBOX_TOKEN},
        map_provider="mapbox",
    )
)
```

## API Documentation

- [Mapbox Isochrone API](https://docs.mapbox.com/api/navigation/isochrone/)
- [Streamlit PyDeck Chart](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart)
- [PyDeck GeoJsonLayer](https://deckgl.readthedocs.io/en/latest/layer.html#pydeck.bindings.layer.Layer)
