import streamlit as st


def validate_mapbox_configured() -> bool:
    """Mapboxトークンが設定されているか確認"""
    try:
        _ = st.secrets.mapbox.token
        return True
    except KeyError, AttributeError:
        return False


def show_mapbox_config_error() -> None:
    """Mapbox未設定エラーの表示"""
    st.error(
        "⚠️ Mapbox access token is not configured. "
        "Please add it to `.streamlit/secrets.toml`:"
    )
    st.code(
        '[mapbox]\ntoken = "your-mapbox-access-token-here"',
        language="toml",
    )
    st.stop()


def require_mapbox_token() -> str:
    """
    Mapboxトークンを取得（設定必須）
    未設定の場合はエラー表示して処理停止
    """
    if not validate_mapbox_configured():
        show_mapbox_config_error()

    return st.secrets.mapbox.token
