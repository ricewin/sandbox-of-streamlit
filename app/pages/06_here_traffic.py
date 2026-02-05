import requests
import streamlit as st
from maplibre.basemaps import Carto
from maplibre.controls import NavigationControl
from maplibre.layer import Layer, LayerType
from maplibre.map import Map, MapOptions
from maplibre.sources import GeoJSONSource
from maplibre.streamlit import st_maplibre

st.title("🚦 HERE Traffic API × MapLibre デモ")

st.markdown(
    """
このデモでは、HERE Traffic APIとMapLibreを組み合わせて、
リアルタイムの交通情報を地図上に可視化します。

### 機能
- 🚗 **交通流量 (Traffic Flow)**: 道路の混雑状況を色で表示
- 🚧 **交通インシデント (Traffic Incidents)**: 事故や工事などの情報を表示
"""
)

# HERE API Key管理
if "here_api_key" not in st.session_state:
    st.session_state.here_api_key = ""

with st.sidebar:
    st.header("🔑 HERE API設定")
    st.markdown(
        """
    HERE APIキーは[HERE Developer Portal](https://developer.here.com/)で取得できます。
    
    **無料プラン**で始められます：
    1. アカウント作成
    2. プロジェクト作成
    3. API Keyを生成
    """
    )

    api_key = st.text_input(
        "HERE API Key",
        value=st.session_state.here_api_key,
        type="password",
        help="HERE Traffic APIを使用するためのAPIキー",
    )

    if api_key:
        st.session_state.here_api_key = api_key
        st.success("✅ APIキーが設定されました")
    else:
        st.warning("⚠️ APIキーを入力してください")

# 地図の中心地点設定
st.subheader("📍 表示地点の設定")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("緯度 (Latitude)", value=35.681236, format="%.6f")
with col2:
    lon = st.number_input("経度 (Longitude)", value=139.767125, format="%.6f")

# サンプル地点ボタン
sample_locations = {
    "東京駅": (35.681236, 139.767125),
    "新宿駅": (35.689487, 139.700675),
    "渋谷駅": (35.658034, 139.701636),
    "大阪駅": (34.702485, 135.495951),
}

st.write("**サンプル地点:**")
cols = st.columns(len(sample_locations))
for idx, (name, (sample_lat, sample_lon)) in enumerate(sample_locations.items()):
    with cols[idx]:
        if st.button(name, key=f"loc_{idx}"):
            st.session_state.sample_lat = sample_lat
            st.session_state.sample_lon = sample_lon
            st.rerun()

if "sample_lat" in st.session_state:
    lat = st.session_state.sample_lat
    lon = st.session_state.sample_lon
    del st.session_state.sample_lat
    del st.session_state.sample_lon


@st.cache_data(ttl=300)  # 5分間キャッシュ
def fetch_traffic_incidents(api_key, lat, lon, radius=5000):
    """HERE Traffic APIから交通インシデント情報を取得"""
    if not api_key:
        return {"type": "FeatureCollection", "features": []}

    base_url = "https://data.traffic.hereapi.com/v7/incidents"

    params = {
        "apiKey": api_key,
        "in": f"circle:{lat},{lon};r={radius}",
        "locationReferencing": "shape",
    }

    try:
        res = requests.get(base_url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        # GeoJSON形式に変換
        features = []
        if "results" in data:
            for incident in data["results"]:
                if "location" in incident and "shape" in incident["location"]:
                    coordinates = [
                        [point["lng"], point["lat"]]
                        for point in incident["location"]["shape"]["links"][0][
                            "points"
                        ]
                    ]

                    # インシデントのタイプと重要度を取得
                    incident_type = (
                        incident.get("incidentDetails", {})
                        .get("type", {})
                        .get("description", "Unknown")
                    )
                    criticality = incident.get("incidentDetails", {}).get(
                        "criticality", {}
                    )

                    features.append(
                        {
                            "type": "Feature",
                            "geometry": {"type": "LineString", "coordinates": coordinates},
                            "properties": {
                                "type": incident_type,
                                "description": incident.get("incidentDetails", {}).get(
                                    "description", {"value": ""}
                                )["value"],
                                "criticality": criticality.get("description", "Unknown"),
                            },
                        }
                    )

        return {"type": "FeatureCollection", "features": features}

    except requests.exceptions.RequestException as e:
        st.error(f"交通情報の取得に失敗しました: {e}")
        return {"type": "FeatureCollection", "features": []}


# デモモード：APIキーがない場合はサンプルデータを表示
if not st.session_state.here_api_key:
    st.info(
        "💡 **デモモード**: APIキーが設定されていないため、サンプルデータを表示します。"
    )

    # サンプルの交通データ（東京周辺の架空データ）
    sample_traffic_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [139.76, 35.68],
                        [139.77, 35.68],
                        [139.78, 35.685],
                    ],
                },
                "properties": {
                    "type": "渋滞",
                    "description": "首都高速道路で渋滞が発生しています",
                    "criticality": "Major",
                    "speed": 15,
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [139.75, 35.67],
                        [139.76, 35.675],
                        [139.77, 35.67],
                    ],
                },
                "properties": {
                    "type": "工事",
                    "description": "道路工事のため車線規制中",
                    "criticality": "Minor",
                    "speed": 30,
                },
            },
        ],
    }

    traffic_geojson = sample_traffic_data
else:
    # 実際のAPIから取得
    with st.spinner("交通情報を取得中..."):
        traffic_geojson = fetch_traffic_incidents(
            st.session_state.here_api_key, lat, lon
        )

# MapLibreで地図を作成
st.subheader("🗺️ 交通情報マップ")

map_options = MapOptions(
    style=Carto.POSITRON,
    center=(lon, lat),
    zoom=13,
    pitch=0,
)  # type: ignore

m = Map(map_options)
m.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

# 交通インシデントレイヤーを追加
if traffic_geojson["features"]:
    traffic_source = GeoJSONSource(data=traffic_geojson)  # pyright: ignore[reportCallIssue]

    # 道路ラインレイヤー
    traffic_layer = Layer(
        type=LayerType.LINE,
        source=traffic_source,
        paint={
            "line-color": [
                "match",
                ["get", "criticality"],
                "Critical",
                "#ff0000",
                "Major",
                "#ff6600",
                "Minor",
                "#ffaa00",
                "#00aa00",  # デフォルト
            ],
            "line-width": 6,
            "line-opacity": 0.8,
        },
    )  # pyright: ignore[reportCallIssue]

    m.add_layer(traffic_layer)

    st_maplibre(m, height=600)

    # インシデント情報を表示
    st.subheader("📋 検出された交通インシデント")
    for idx, feature in enumerate(traffic_geojson["features"], 1):
        props = feature["properties"]
        with st.expander(f"{idx}. {props.get('type', 'Unknown')} - {props.get('criticality', 'Unknown')}"):
            st.write(f"**詳細**: {props.get('description', '情報なし')}")
            if "speed" in props:
                st.write(f"**速度**: 約 {props['speed']} km/h")
else:
    st_maplibre(m, height=600)
    st.info("この地域には現在交通インシデントが検出されていません。")

# 使い方の説明
st.divider()
st.markdown(
    """
### 📖 使い方

1. **APIキーの取得**
   - [HERE Developer Portal](https://developer.here.com/)でアカウントを作成
   - 新しいプロジェクトを作成し、API Keyを生成
   - サイドバーにAPIキーを入力

2. **地点の選択**
   - サンプル地点ボタンで主要都市を選択、または
   - 緯度・経度を直接入力してカスタム地点を表示

3. **交通情報の確認**
   - 地図上の色付きラインが交通インシデントを示します
   - **赤**: 重大な渋滞・事故
   - **オレンジ**: 中程度の渋滞
   - **黄色**: 軽度の影響
   - 各インシデントの詳細は下部のリストで確認できます

### 🎓 学習ポイント

- **HERE Traffic API**: リアルタイムの交通情報を提供する強力なAPI
- **MapLibre**: オープンソースの地図ライブラリで、カスタマイズ性が高い
- **GeoJSON**: 地理情報を標準化された形式で扱う
- **Streamlit Caching**: APIレスポンスをキャッシュしてパフォーマンス向上

### 🔗 参考リンク

- [HERE Traffic API Documentation](https://developer.here.com/documentation/traffic-api/dev_guide/index.html)
- [MapLibre GL JS](https://maplibre.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### 💡 応用アイデア

このチュートリアルを基に、以下のような機能を追加できます：
- 複数地点の交通情報を同時に表示
- 時系列での交通パターン分析
- ルート案内と交通情報の組み合わせ
- リアルタイム更新（自動更新機能）
- 交通情報のエクスポート機能
"""
)
