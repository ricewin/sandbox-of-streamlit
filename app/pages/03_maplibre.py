import streamlit as st
from maplibre.basemaps import Carto
from maplibre.controls import Marker, NavigationControl
from maplibre.layer import Layer, LayerType
from maplibre.map import Map, MapOptions
from maplibre.sources import GeoJSONSource
from maplibre.streamlit import st_maplibre

st.title("🗺️ MapLibre マップ表示サンプル集")

st.markdown(
    """
MapLibreで利用できる様々な表現方法のサンプル集です。
各タブで異なる表現を確認できます。
"""
)

# タブを作成
tabs = st.tabs(
    [
        "🎯 基本マーカー",
        "🔵 Circle Layer",
        "🔥 Heatmap",
        "📏 Line Layer",
        "🏢 Fill Layer",
        "🏗️ 3D Extrusion",
        "🎨 複数スタイル",
    ]
)

# タブ1: 基本マーカー
with tabs[0]:
    st.subheader("基本的なマーカー表示")
    st.write("マーカーとNavigationControlを使った基本的な地図表示")

    map_options = MapOptions(
        style=Carto.POSITRON,
        center=(139.767, 35.681),  # 東京駅
        zoom=12,
        pitch=0,
    )  # type: ignore

    m1 = Map(map_options)
    m1.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

    # 複数のマーカーを追加
    locations = [
        (139.767, 35.681),  # 東京駅
        (139.7, 35.658),  # 六本木
        (139.8, 35.7),  # スカイツリー
    ]

    for lng, lat in locations:
        marker = Marker(lng_lat=(lng, lat))
        m1.add_marker(marker)

    st_maplibre(m1, height=500)

# タブ2: Circle Layer
with tabs[1]:
    st.subheader("Circle Layer - データポイントの可視化")
    st.write("円の大きさや色でデータを視覚化")

    map_options = MapOptions(
        style=Carto.DARK_MATTER,
        center=(139.767, 35.681),
        zoom=11,
    )  # type: ignore

    m2 = Map(map_options)
    m2.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

    # ランダムなポイントデータを生成
    circle_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [139.767 + i * 0.02, 35.681 + j * 0.02],
                },
                "properties": {"value": (i + 1) * (j + 1) * 10},
            }
            for i in range(-3, 4)
            for j in range(-3, 4)
        ],
    }

    circle_source = GeoJSONSource(data=circle_data)  # pyright: ignore[reportCallIssue]

    circle_layer = Layer(
        type=LayerType.CIRCLE,
        source=circle_source,
        paint={
            "circle-radius": ["*", ["get", "value"], 0.3],  # 値に応じて半径を変更
            "circle-color": [
                "interpolate",
                ["linear"],
                ["get", "value"],
                0,
                "#ffffcc",
                50,
                "#ff9900",
                100,
                "#ff0000",
            ],
            "circle-opacity": 0.8,
            "circle-stroke-width": 2,
            "circle-stroke-color": "#ffffff",
        },
    )  # pyright: ignore[reportCallIssue]

    m2.add_layer(circle_layer)
    st_maplibre(m2, height=500)

# タブ3: Heatmap
with tabs[2]:
    st.subheader("Heatmap - 密度の可視化")
    st.write("データの密度をヒートマップで表現")

    map_options = MapOptions(
        style=Carto.DARK_MATTER,
        center=(139.767, 35.681),
        zoom=11,
    )  # type: ignore

    m3 = Map(map_options)
    m3.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

    # ヒートマップ用のポイントデータ
    heatmap_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [139.767 + i * 0.005, 35.681 + j * 0.005],
                },
                "properties": {"intensity": 1},
            }
            for i in range(-20, 21)
            for j in range(-20, 21)
            if abs(i) + abs(j) < 15  # 円形の分布
        ],
    }

    heatmap_source = GeoJSONSource(
        data=heatmap_data
    )  # pyright: ignore[reportCallIssue]

    heatmap_layer = Layer(
        type=LayerType.HEATMAP,
        source=heatmap_source,
        paint={
            "heatmap-weight": ["get", "intensity"],
            "heatmap-intensity": 1.5,
            "heatmap-color": [
                "interpolate",
                ["linear"],
                ["heatmap-density"],
                0,
                "rgba(33,102,172,0)",
                0.2,
                "rgb(103,169,207)",
                0.4,
                "rgb(209,229,240)",
                0.6,
                "rgb(253,219,199)",
                0.8,
                "rgb(239,138,98)",
                1,
                "rgb(178,24,43)",
            ],
            "heatmap-radius": 30,
        },
    )  # pyright: ignore[reportCallIssue]

    m3.add_layer(heatmap_layer)
    st_maplibre(m3, height=500)

# タブ4: Line Layer
with tabs[3]:
    st.subheader("Line Layer - ルート・境界線の表示")
    st.write("線で経路や境界を表現")

    map_options = MapOptions(
        style=Carto.VOYAGER,
        center=(139.767, 35.681),
        zoom=12,
    )  # type: ignore

    m4 = Map(map_options)
    m4.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

    # ライン用のデータ（山手線を簡略化したルート）
    line_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [139.767, 35.681],  # 東京
                        [139.777, 35.665],  # 有楽町方面
                        [139.740, 35.655],  # 新橋方面
                        [139.730, 35.648],  # 浜松町方面
                        [139.747, 35.630],  # 品川方面
                        [139.700, 35.632],  # 渋谷方面
                        [139.702, 35.694],  # 新宿方面
                        [139.728, 35.731],  # 池袋方面
                        [139.771, 35.730],  # 上野方面
                        [139.767, 35.681],  # 東京に戻る
                    ],
                },
                "properties": {"name": "ルートサンプル"},
            }
        ],
    }

    line_source = GeoJSONSource(data=line_data)  # pyright: ignore[reportCallIssue]

    line_layer = Layer(
        type=LayerType.LINE,
        source=line_source,
        paint={
            "line-color": "#00aa00",
            "line-width": 4,
            "line-opacity": 0.8,
            "line-dasharray": [2, 2],  # 破線
        },
    )  # pyright: ignore[reportCallIssue]

    m4.add_layer(line_layer)
    st_maplibre(m4, height=500)

# タブ5: Fill Layer
with tabs[4]:
    st.subheader("Fill Layer - エリア・ポリゴンの表示")
    st.write("塗りつぶしでエリアを表現")

    map_options = MapOptions(
        style=Carto.POSITRON,
        center=(139.767, 35.681),
        zoom=11,
    )  # type: ignore

    m5 = Map(map_options)
    m5.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

    # ポリゴンデータ（エリアを表現）
    polygon_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [139.75, 35.67],
                            [139.78, 35.67],
                            [139.78, 35.69],
                            [139.75, 35.69],
                            [139.75, 35.67],
                        ]
                    ],
                },
                "properties": {"name": "エリア1", "density": 100},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [139.76, 35.65],
                            [139.79, 35.65],
                            [139.79, 35.67],
                            [139.76, 35.67],
                            [139.76, 35.65],
                        ]
                    ],
                },
                "properties": {"name": "エリア2", "density": 200},
            },
        ],
    }

    polygon_source = GeoJSONSource(
        data=polygon_data
    )  # pyright: ignore[reportCallIssue]

    fill_layer = Layer(
        type=LayerType.FILL,
        source=polygon_source,
        paint={
            "fill-color": [
                "interpolate",
                ["linear"],
                ["get", "density"],
                0,
                "#ffffcc",
                100,
                "#78c679",
                200,
                "#006837",
            ],
            "fill-opacity": 0.5,
        },
    )  # pyright: ignore[reportCallIssue]

    # 境界線レイヤーも追加
    outline_layer = Layer(
        type=LayerType.LINE,
        source=polygon_source,
        paint={
            "line-color": "#000000",
            "line-width": 2,
        },
    )  # pyright: ignore[reportCallIssue]

    m5.add_layer(fill_layer)
    m5.add_layer(outline_layer)
    st_maplibre(m5, height=500)

# タブ6: 3D Extrusion
with tabs[5]:
    st.subheader("Fill Extrusion - 3Dビル表現")
    st.write("高さを持った3D表現（ビルなど）")

    map_options = MapOptions(
        style=Carto.DARK_MATTER,
        center=(139.767, 35.681),
        zoom=14,
        pitch=60,  # 3D視点
        bearing=20,
    )  # type: ignore

    m6 = Map(map_options)
    m6.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

    # ビル用のポリゴンデータ（高さ情報付き）
    building_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [139.765, 35.680],
                            [139.766, 35.680],
                            [139.766, 35.681],
                            [139.765, 35.681],
                            [139.765, 35.680],
                        ]
                    ],
                },
                "properties": {"height": 150},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [139.768, 35.681],
                            [139.769, 35.681],
                            [139.769, 35.682],
                            [139.768, 35.682],
                            [139.768, 35.681],
                        ]
                    ],
                },
                "properties": {"height": 200},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [139.767, 35.679],
                            [139.768, 35.679],
                            [139.768, 35.680],
                            [139.767, 35.680],
                            [139.767, 35.679],
                        ]
                    ],
                },
                "properties": {"height": 100},
            },
        ],
    }

    building_source = GeoJSONSource(
        data=building_data
    )  # pyright: ignore[reportCallIssue]

    extrusion_layer = Layer(
        type=LayerType.FILL_EXTRUSION,
        source=building_source,
        paint={
            "fill-extrusion-color": [
                "interpolate",
                ["linear"],
                ["get", "height"],
                0,
                "#ffeda0",
                100,
                "#f03b20",
                200,
                "#bd0026",
            ],
            "fill-extrusion-height": ["get", "height"],
            "fill-extrusion-base": 0,
            "fill-extrusion-opacity": 0.9,
        },
    )  # pyright: ignore[reportCallIssue]

    m6.add_layer(extrusion_layer)
    st_maplibre(m6, height=500)

# タブ7: 複数スタイル比較
with tabs[6]:
    st.subheader("ベースマップスタイル比較")
    st.write("利用可能な地図スタイルの一覧")

    col1, col2 = st.columns(2)

    styles = [
        (Carto.POSITRON, "Positron（明るい）"),
        (Carto.DARK_MATTER, "Dark Matter（暗い）"),
        (Carto.VOYAGER, "Voyager（標準）"),
    ]

    for idx, (style, name) in enumerate(styles):
        with col1 if idx % 2 == 0 else col2:
            st.write(f"**{name}**")
            map_options = MapOptions(
                style=style,
                center=(139.767, 35.681),
                zoom=12,
            )  # type: ignore

            m_style = Map(map_options)
            m_style.add_control(NavigationControl())  # pyright: ignore[reportCallIssue]

            marker = Marker(lng_lat=(139.767, 35.681))
            m_style.add_marker(marker)

            st_maplibre(m_style, height=300)

st.divider()
st.markdown(
    """
### 🎓 学習ポイント
- **Circle Layer**: データポイントの密度や値を円で表現
- **Heatmap**: データの集中度を色のグラデーションで表現
- **Line Layer**: ルートや境界線を線で表現
- **Fill Layer**: エリアやポリゴンを塗りつぶしで表現
- **Fill Extrusion**: 3D表現でビルや高さ情報を表現
- **Style**: 用途に応じてベースマップを選択可能

各レイヤーの`paint`プロパティで、色・サイズ・透明度などを細かく制御できます。
"""
)
