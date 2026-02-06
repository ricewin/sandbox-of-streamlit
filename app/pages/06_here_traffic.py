import requests
import streamlit as st
from maplibre.basemaps import Carto
from maplibre.controls import NavigationControl
from maplibre.layer import Layer, LayerType
from maplibre.map import Map, MapOptions
from maplibre.sources import GeoJSONSource
from maplibre.streamlit import st_maplibre


def calculate_speed_percentage(speed, free_flow):
    """現在速度の自由流速度に対するパーセンテージを計算"""
    if free_flow and free_flow > 0:
        return (speed / free_flow) * 100
    return 100.0


def evaluate_jam_factor(jam_factor):
    """渋滞係数を評価レベルに変換"""
    if jam_factor is None:
        return "不明"
    if jam_factor <= 2.0:
        return "軽い"
    elif jam_factor <= 6.0:
        return "中程度"
    else:
        return "重大"


def get_functional_class_name(functional_class):
    """道路等級IDを日本語名に変換"""
    mapping = {
        1: "高速道路",
        2: "主要幹線道路",
        3: "補助幹線道路",
        4: "生活道路",
        5: "住宅道路",
    }
    return mapping.get(functional_class, "その他")


st.title("🚦 HERE Traffic API × MapLibre デモ")

st.markdown(
    """
このデモでは、HERE Traffic APIとMapLibreを組み合わせて、
リアルタイムの交通情報を地図上に可視化します。

### 機能
- 🚗 **交通流量 (Traffic Flow)**: 道路の混雑状況を色で表示
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

with st.container(horizontal=True):
    lat = st.number_input("緯度 (Latitude)", value=35.681236, format="%.6f")
    lon = st.number_input("経度 (Longitude)", value=139.767125, format="%.6f")

# サンプル地点ボタン（交通量の多い主要都市）
sample_locations = {
    "東京駅": (35.681236, 139.767125),
    "大阪梅田": (34.702485, 135.495951),
    "名古屋駅": (35.170915, 136.881537),
    "福岡天神": (33.590355, 130.401716),
    "札幌駅": (43.068661, 141.350755),
}

st.write("**サンプル地点:**")
with st.container(horizontal=True):
    for idx, (name, (sample_lat, sample_lon)) in enumerate(sample_locations.items()):
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
def fetch_traffic_flow(api_key, lat, lon, radius=5000):
    """HERE Traffic APIから交通流量情報を取得"""
    if not api_key:
        return {"type": "FeatureCollection", "features": []}

    base_url = "https://data.traffic.hereapi.com/v7/flow"

    params = {
        "in": f"circle:{lat},{lon};r={radius}",
        "locationReferencing": "shape",
        "apiKey": api_key,
    }

    try:
        res = requests.get(base_url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        # GeoJSON形式に変換
        features = []
        if "results" in data:
            for result in data["results"]:
                current_flow = result.get("currentFlow", {})
                location = result.get("location", {})

                # 座標データの取得
                if "shape" in location and "links" in location["shape"]:
                    links = location["shape"]["links"]
                    if links and "points" in links[0]:
                        coordinates = [
                            [point["lng"], point["lat"]] for point in links[0]["points"]
                        ]

                        # 速度データ（APIレスポンスはm/s - 表示用にkm/hに変換）
                        # HERE Traffic APIのspeed, freeFlow, speedUncappedはすべてメートル/秒
                        speed = current_flow.get("speed", 0) * 3.6  # m/s を km/h に変換
                        free_flow = (
                            current_flow.get("freeFlow", 0) * 3.6
                        )  # m/s を km/h に変換
                        speed_uncapped = (
                            current_flow.get("speedUncapped", 0) * 3.6
                        )  # m/s を km/h に変換
                        jam_factor = current_flow.get("jamFactor", 0)
                        confidence = current_flow.get("confidence", 1.0)
                        traversability = current_flow.get("traversability", "open")

                        # パーセンテージと評価
                        speed_percentage = calculate_speed_percentage(speed, free_flow)
                        congestion_level = evaluate_jam_factor(jam_factor)
                        is_confidence_low = confidence < 0.7

                        # 道路セグメント情報
                        length = location.get("length", 0)
                        functional_class = links[0].get("functionalClass", 0)
                        functional_class_name = get_functional_class_name(
                            functional_class
                        )

                        # サブセグメント数のカウント
                        sub_segments = current_flow.get("subSegments", [])
                        sub_segment_count = len(sub_segments)

                        features.append(
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": coordinates,
                                },
                                "properties": {
                                    # 速度情報
                                    "speed": round(speed, 1),
                                    "freeFlow": round(free_flow, 1),
                                    "speedUncapped": round(speed_uncapped, 1),
                                    "speedPercentage": round(speed_percentage, 1),
                                    # 混雑情報
                                    "jamFactor": round(jam_factor, 2),
                                    "congestionLevel": congestion_level,
                                    # 信頼度
                                    "confidence": round(confidence, 2),
                                    "isConfidenceLow": is_confidence_low,
                                    # 道路情報
                                    "length": length,
                                    "functionalClass": functional_class,
                                    "functionalClassName": functional_class_name,
                                    "traversability": traversability,
                                    # セグメント情報
                                    "subSegmentCount": sub_segment_count,
                                },
                            }
                        )

        return {"type": "FeatureCollection", "features": features}

    except requests.exceptions.RequestException as e:
        # エラーは返り値で呼び出し元に伝え、キャッシュ外で表示を行う
        return {
            "type": "FeatureCollection",
            "features": [],
            "error": f"交通情報の取得に失敗しました: {e}",
        }


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
                    "speed": 50.0,
                    "freeFlow": 100.0,
                    "speedUncapped": 120.0,
                    "speedPercentage": 83.3,
                    "jamFactor": 7.5,
                    "congestionLevel": "重大",
                    "confidence": 0.9,
                    "isConfidenceLow": False,
                    "length": 1850,
                    "functionalClass": 1,
                    "functionalClassName": "高速道路",
                    "traversability": "open",
                    "subSegmentCount": 3,
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
                    "speed": 40.8,
                    "freeFlow": 60.0,
                    "speedUncapped": 79.8,
                    "speedPercentage": 60.0,
                    "jamFactor": 4.2,
                    "congestionLevel": "中程度",
                    "confidence": 0.85,
                    "isConfidenceLow": False,
                    "length": 920,
                    "functionalClass": 2,
                    "functionalClassName": "主要幹線道路",
                    "traversability": "open",
                    "subSegmentCount": 1,
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [139.79, 35.69],
                        [139.80, 35.695],
                    ],
                },
                "properties": {
                    "speed": 40.4,
                    "freeFlow": 50.0,
                    "speedUncapped": 60.4,
                    "speedPercentage": 80.0,
                    "jamFactor": 1.2,
                    "congestionLevel": "軽い",
                    "confidence": 0.65,
                    "isConfidenceLow": True,
                    "length": 450,
                    "functionalClass": 3,
                    "functionalClassName": "補助幹線道路",
                    "traversability": "open",
                    "subSegmentCount": 0,
                },
            },
        ],
    }

    traffic_geojson = sample_traffic_data
else:
    # 実際のAPIから取得
    with st.spinner("交通情報を取得中..."):
        traffic_geojson = fetch_traffic_flow(st.session_state.here_api_key, lat, lon)
    
    # エラーハンドリング（キャッシュの外）
    if "error" in traffic_geojson:
        st.error(traffic_geojson["error"])
    
    # デバッグ用：レスポンスの一部を表示（キャッシュの外）
    if traffic_geojson["features"]:
        with st.expander("🔍 取得データ数", expanded=False):
            st.caption(f"取得した交通流量データ: {len(traffic_geojson['features'])} 件")

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

# 交通流量レイヤーを追加
if traffic_geojson["features"]:
    traffic_source = GeoJSONSource(data=traffic_geojson)  # pyright: ignore[reportCallIssue]

    # 道路ラインレイヤー（渋滞係数に基づいて色分け）
    traffic_layer = Layer(
        type=LayerType.LINE,
        source=traffic_source,
        paint={
            "line-color": [
                "step",
                ["get", "jamFactor"],
                "#00aa00",  # jamFactor <= 2.0: 緑（軽い）
                2.0,
                "#ffaa00",  # jamFactor <= 6.0: 黄色（中程度）
                6.0,
                "#ff0000",  # jamFactor > 6.0: 赤（重大）
            ],
            "line-width": 6,
            "line-opacity": 0.8,
        },
    )  # pyright: ignore[reportCallIssue]

    m.add_layer(traffic_layer)

    st_maplibre(m, height=600)

    # 交通情報を表示
    st.subheader("📋 検出された交通流量情報")
    for idx, feature in enumerate(traffic_geojson["features"], 1):
        props = feature["properties"]

        # タイトル：混雑レベルと道路種別
        congestion = props.get("congestionLevel", "不明")
        road_type = props.get("functionalClassName", "不明")
        jam_factor = props.get("jamFactor", 0)

        # 混雑レベルに応じたアイコン
        if congestion == "重大":
            icon = "🔴"
        elif congestion == "中程度":
            icon = "🟡"
        else:
            icon = "🟢"

        with st.expander(
            f"{icon} {idx}. {road_type} - {congestion} (渋滞係数: {jam_factor})"
        ):
            # 速度情報セクション
            st.markdown("### 🚗 速度情報")
            with st.container(horizontal=True):
                st.metric(
                    "現在速度",
                    f"{props.get('speed', 0):.1f} km/h",
                )

                st.metric(
                    "自由流速度",
                    f"{props.get('freeFlow', 0):.1f} km/h",
                )

                speed_pct = props.get("speedPercentage", 100)
                st.metric(
                    "速度比率",
                    f"{speed_pct:.1f}%",
                    delta=f"{speed_pct - 100:.1f}%" if speed_pct < 100 else None,
                    delta_color="inverse",
                )

            # 混雑情報セクション
            st.markdown("### 🚦 混雑情報")
            with st.container(horizontal=True):
                st.write(f"**渋滞係数**: {jam_factor:.2f} / 10.0")
                st.write(f"**混雑レベル**: {congestion}")

                confidence = props.get("confidence", 1.0)
                st.write(f"**データ信頼度**: {confidence * 100:.0f}%")
                if props.get("isConfidenceLow", False):
                    st.warning("⚠️ 信頼度が低い可能性があります")

            # 道路セグメント情報
            st.markdown("### 🛣️ 道路情報")
            with st.container(horizontal=True):
                length = props.get("length", 0)
                st.write(f"**セグメント長**: {length:,} m")

                st.write(f"**道路等級**: {road_type}")

                sub_count = props.get("subSegmentCount", 0)
                if sub_count > 0:
                    st.write(f"**サブセグメント**: {sub_count} 箇所")
                else:
                    st.write("**サブセグメント**: なし")

            # 通行可能性
            traversability = props.get("traversability", "unknown")
            if traversability == "open":
                st.success("✅ 通行可能")
            else:
                st.error(f"❌ 通行状態: {traversability}")
else:
    st_maplibre(m, height=600)
    st.info("この地域には現在交通流量情報が検出されていません。")

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
    - 地図上の色付きラインが交通流量（渋滞状況）を示します
    - **赤**: 重大な渋滞（渋滞係数 > 6.0）
    - **黄**: 中程度の渋滞（渋滞係数 2.0 - 6.0）
    - **緑**: 通常の流れ（渋滞係数 < 2.0）
    - 各道路セグメントの詳細は下部のリストで確認できます

### 🎓 学習ポイント

- **HERE Traffic Flow API**: リアルタイムの交通流量情報を提供する強力なAPI
  - **速度の単位**: API レスポンスはメートル/秒（m/s）で返却され、表示用に km/h に変換
  - **speed**: 現在の道路速度（m/s）
  - **freeFlow**: 交通量がない時の基準速度（m/s）
  - **speedUncapped**: 法定速度制限を超える場合がある予想速度（m/s）
  - **jamFactor**: 渋滞係数（0-10、値が大きいほど渋滞）
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
