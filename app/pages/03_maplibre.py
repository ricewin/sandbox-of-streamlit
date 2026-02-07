import streamlit as st
from maplibre.basemaps import Carto
from maplibre.controls import NavigationControl
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

    # 複数のマーカーを追加（GeoJSONで管理してツールチップを表示）
    marker_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [139.767, 35.681],
                },
                "properties": {"name": "東京駅", "description": "東京の中心駅"},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [139.7, 35.658],
                },
                "properties": {"name": "六本木", "description": "商業・娯楽エリア"},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [139.8, 35.7],
                },
                "properties": {
                    "name": "スカイツリー",
                    "description": "高さ634mのタワー",
                },
            },
        ],
    }

    def create_marker_layer(data: dict) -> dict:
        return {
            "@@type": "GeoJsonLayer",
            "id": "MarkerLayer",
            "data": data,
            "pickable": True,
            "stroked": True,
            "filled": True,
            "lineWidthMinPixels": 2,
            "getRadius": 200,
            "getFillColor": [56, 135, 190, 200],
            "getLineColor": [255, 255, 255],
        }

    m1.add_deck_layers(
        [create_marker_layer(marker_data)],
        tooltip="Name: {{ properties.name }}, Description: {{ properties.description }}",
    )
    st_maplibre(m1, height=500)

    # マーカー情報の表示
    st.info(
        "📍 **マーカー情報**: 東京駅（東京の中心駅）、六本木（商業・娯楽エリア）、スカイツリー（高さ634mのタワー）"
    )

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

    def create_circle_layer(data: dict) -> dict:
        return {
            "@@type": "GeoJsonLayer",
            "id": "CircleLayer",
            "data": data,
            "pickable": True,
            "stroked": True,
            "filled": True,
            "lineWidthMinPixels": 2,
            "getRadius": "@@=properties.value",
            "getFillColor": [255, 0, 0, 100],
            "getLineColor": [255, 255, 255],
        }

    m2.add_deck_layers(
        [create_circle_layer(circle_data)],
        tooltip="Value: {{ properties.value }}",
    )
    st_maplibre(m2, height=500)

    st.info(
        "💡 **表示内容**: 円の大きさと色が値を表しています。値が大きいほど円が大きく、色が赤くなります。マウスホバーでツールチップを表示します。"
    )

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
            for i in range(-14, 15)
            for j in range(-(14 - abs(i)), (14 - abs(i)) + 1)
            # abs(i) + abs(j) <= 14 を満たす整数点のみを生成（ひし形の分布）
        ],
    }

    heatmap_source = GeoJSONSource(data=heatmap_data)  # pyright: ignore[reportCallIssue]

    heatmap_layer = Layer(
        id="HeatmapLayer",
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

    st.info("🔥 **ヒートマップ**: データの密度が高い場所ほど赤く表示されます。")

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
        id="LineLayer",
        type=LayerType.LINE,
        source=line_source,
        paint={
            "line-color": "#00aa00",
            "line-width": 4,
            "line-opacity": 0.8,
            "line-dasharray": [4, 2],
        },
    )  # pyright: ignore[reportCallIssue]

    m4.add_layer(line_layer)
    st_maplibre(m4, height=500)

    st.info("🛣️ **ルート**: 山手線を簡略化したルートを破線で表示しています。")

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

    def create_fill_layer(data: dict) -> dict:
        return {
            "@@type": "GeoJsonLayer",
            "id": "FillLayer",
            "data": data,
            "pickable": True,
            "stroked": True,
            "filled": True,
            "wireframe": False,
            "getFillColor": [76, 175, 80, 200],
            "getLineColor": [0, 0, 0],
            "getLineWidth": 2,
        }

    m5.add_deck_layers(
        [create_fill_layer(polygon_data)],
        tooltip="Name: {{ properties.name }}, Density: {{ properties.density }}",
    )
    st_maplibre(m5, height=500)

    st.info(
        "🏢 **エリア情報**: エリア1（密度100）とエリア2（密度200）。マウスホバーでエリア情報を確認できます。"
    )

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
                "properties": {"height": 150, "name": "ビル1"},
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
                "properties": {"height": 200, "name": "ビル2"},
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
                "properties": {"height": 100, "name": "ビル3"},
            },
        ],
    }

    def create_extrusion_layer(data: dict) -> dict:
        return {
            "@@type": "GeoJsonLayer",
            "id": "ExtrusionLayer",
            "data": data,
            "pickable": True,
            "stroked": True,
            "filled": True,
            "extruded": True,
            "wireframe": False,
            "getElevation": "@@=properties.height * 10",
            "getFillColor": [200, 100, 50, 200],
            "getLineColor": [255, 255, 255],
            "getLineWidth": 1,
        }

    m6.add_deck_layers(
        [create_extrusion_layer(building_data)],
        tooltip="Name: {{ properties.name }}, Height: {{ properties.height }}m",
    )
    st_maplibre(m6, height=500)

    st.info(
        "🏗️ **3Dビル**: 高さ100m、150m、200mの3つのビルを3D表示。マウスホバーでビル情報を確認できます。"
    )

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

            # ツールチップ付きマーカー
            style_marker_data = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [139.767, 35.681],
                        },
                        "properties": {"name": "東京駅", "style": name},
                    }
                ],
            }

            def create_style_marker_layer(data: dict) -> dict:
                return {
                    "@@type": "GeoJsonLayer",
                    "id": "StyleMarkerLayer",
                    "data": data,
                    "pickable": True,
                    "stroked": True,
                    "filled": True,
                    "lineWidthMinPixels": 2,
                    "getRadius": 200,
                    "getFillColor": [56, 135, 190, 200],
                    "getLineColor": [255, 255, 255],
                }

            m_style.add_deck_layers(
                [create_style_marker_layer(style_marker_data)],
                tooltip="Station: {{ properties.name }}",
            )

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
各タブの地図下に表示される情報で、データの内容を確認できます。
"""
)
