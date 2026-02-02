# Shapefile Visualization with PyDeck

## 概要 (Overview)

このページでは、PyDeck の GeoJsonLayer を使用してシェープファイルを可視化する方法を実装しています。

This page demonstrates how to visualize shapefiles using PyDeck's GeoJsonLayer.

## 機能 (Features)

### サポートされるフォーマット (Supported Formats)

1. **Shapefile** (.shp + .shx + .dbf + .prj)
   - 複数のファイルを一括でアップロード
   - 自動的に GeoJSON 形式に変換
   - WGS84 (EPSG:4326) への座標系変換

2. **GeoJSON** (.geojson / .json)
   - 単一ファイルでアップロード
   - 直接読み込みが可能

### 主な機能 (Main Features)

- ✅ Shapefile 形式の直接読み込み
- ✅ GeoJSON 形式の読み込み
- ✅ 自動的な座標系変換 (WGS84)
- ✅ インタラクティブな地図表示
- ✅ 属性情報のツールチップ表示
- ✅ カスタマイズ可能なスタイル設定
- ✅ サンプルデータによるデモ

## 実装方法 (Implementation)

### 使用ライブラリ (Libraries Used)

```python
import geopandas as gpd  # Shapefile と GeoJSON の読み込み
import pydeck as pdk     # 地図可視化
import streamlit as st   # Web インターフェース
```

### 主要な処理フロー (Main Process Flow)

1. **Shapefile の読み込み**
   ```python
   gdf = gpd.read_file("path/to/shapefile.shp")
   ```

2. **座標系の変換 (必要に応じて)**
   ```python
   if gdf.crs.to_epsg() != 4326:
       gdf = gdf.to_crs(epsg=4326)
   ```

3. **GeoJSON 形式への変換**
   ```python
   geojson_data = gdf.__geo_interface__
   ```

4. **PyDeck での可視化**
   ```python
   layer = pdk.Layer(
       "GeoJsonLayer",
       geojson_data,
       pickable=True,
       # スタイル設定
   )
   ```

## 技術的な詳細 (Technical Details)

### Shapefile の構成要素

Shapefile は以下のファイルで構成されています：

- `.shp` - ジオメトリデータ (必須)
- `.shx` - インデックスファイル (必須)
- `.dbf` - 属性データ (必須)
- `.prj` - 座標系情報 (オプションだが推奨)

### GeoJSON への変換理由

PyDeck の `GeoJsonLayer` は名前の通り GeoJSON 形式を要求します。
Shapefile を直接使用することはできないため、以下の手順で変換します：

1. GeoPandas でシェープファイルを読み込み
2. GeoDataFrame を GeoJSON 形式に変換
3. PyDeck の GeoJsonLayer に渡す

### 座標系について

Web マップでは通常 WGS84 (EPSG:4326) が使用されるため、
他の座標系のデータは自動的に変換されます。

## 使用方法 (How to Use)

### 1. サンプルデータで試す

サイドバーで "Sample Data" を選択すると、Natural Earth の国境データが表示されます。

### 2. Shapefile をアップロード

1. サイドバーで "Upload Shapefile" を選択
2. 以下のファイルをアップロード：
   - .shp ファイル (必須)
   - .shx ファイル (必須)
   - .dbf ファイル (必須)
   - .prj ファイル (オプション)

### 3. GeoJSON をアップロード

1. サイドバーで "Upload GeoJSON" を選択
2. .geojson または .json ファイルをアップロード

### 4. スタイルのカスタマイズ

サイドバーで以下を調整できます：
- 塗りつぶし色 (Fill Color)
- 線の色 (Line Color)
- 不透明度 (Opacity)

## サンプルコード (Sample Code)

### 基本的な使用例

```python
import geopandas as gpd
import pydeck as pdk

# Shapefile を読み込み
gdf = gpd.read_file("data.shp")

# WGS84 に変換
if gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# GeoJSON に変換
geojson = gdf.__geo_interface__

# PyDeck レイヤーを作成
layer = pdk.Layer(
    "GeoJsonLayer",
    geojson,
    pickable=True,
    opacity=0.5,
    get_fill_color=[255, 235, 215],
    get_line_color=[255, 250, 205],
)

# 地図を表示
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=35.6,
        longitude=139.7,
        zoom=10
    )
)
```

## 参考リンク (References)

- [PyDeck Documentation](https://deckgl.readthedocs.io/)
- [GeoJsonLayer](https://deck.gl/docs/api-reference/layers/geojson-layer)
- [GeoPandas Documentation](https://geopandas.org/)
- [Shapefile Format](https://en.wikipedia.org/wiki/Shapefile)

## 注意事項 (Notes)

- 大きなシェープファイルは処理に時間がかかる場合があります
- ファイルサイズの上限に注意してください
- すべてのシェープファイルコンポーネントは同じベース名である必要があります
- Web アプリケーションでは GeoJSON 形式の方が扱いやすい場合があります

## トラブルシューティング (Troubleshooting)

### エラー: "CRS not found"

`.prj` ファイルをアップロードしてください。座標系情報が必要です。

### エラー: "File not found"

すべての必須ファイル (.shp, .shx, .dbf) がアップロードされているか確認してください。

### 地図が正しく表示されない

- 座標系が正しいか確認
- ジオメトリタイプがサポートされているか確認 (Polygon, MultiPolygon)
- データの範囲が適切か確認
