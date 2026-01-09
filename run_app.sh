#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/app/main.py"
uv run streamlit run "$APP_PATH" --server.enableCORS=false --server.enableXsrfProtection=false
