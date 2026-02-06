# HERE Traffic Flow API × MapLibre チュートリアル

このチュートリアルでは、HERE Traffic Flow APIとMapLibreを組み合わせて、リアルタイムの交通流量情報を地図上に可視化する方法を学びます。

## 🎯 チュートリアルの目的

交通流量APIと地図ライブラリを統合して、実用的な交通可視化アプリケーションを作成します。

### 学習内容

- HERE Traffic Flow APIの基本的な使い方
- MapLibreでのGeoJSONデータの表示
- Streamlitでのインタラクティブな地図アプリケーション作成
- APIレスポンスのキャッシング戦略

## 📋 前提条件

- Python 3.14以上
- Streamlitの基本知識
- 地図とGeoJSONの基本的な理解

## 🚀 セットアップ

### 1. HERE Developer Accountの作成

1. [HERE Developer Portal](https://developer.here.com/)にアクセス
2. 無料アカウントを作成（クレジットカード不要）
3. 新しいプロジェクトを作成
4. API Keyを生成

**無料プラン**:
- 月間250,000トランザクションまで無料
- Traffic APIを含む主要なAPIにアクセス可能

### 2. APIキーの設定

2つの方法でAPIキーを設定できます：

#### 方法1: アプリケーション内で入力（推奨）
- サイドバーのテキストフィールドにAPIキーを入力
- セッション中のみ有効

#### 方法2: Streamlit Secretsを使用
`.streamlit/secrets.toml`を作成：
```toml
[here]
api_key = "your_here_api_key_here"
```

## 🎨 チュートリアルの内容

### 実装される機能

1. **交通流量の取得**
   - HERE Traffic Flow APIを使用してリアルタイムデータを取得
   - 道路速度、渋滞係数、自由流速度などの情報を収集

2. **地図上での可視化**
   - MapLibreを使用してインタラクティブな地図を表示
   - 渋滞係数に応じた色分け表示（赤: 重大、黄: 中程度、緑: 軽い）
   - カスタマイズ可能なスタイル

3. **インタラクティブUI**
   - 地点選択機能（サンプル地点 + カスタム座標）
   - リアルタイム情報更新
   - 道路セグメント詳細の表示

4. **パフォーマンス最適化**
   - APIレスポンスのキャッシング（5分間）
   - エラーハンドリング
   - デモモード（APIキーなしでもサンプルデータで動作）

## 📝 コードの主要部分

### HERE Traffic Flow API統合

```python
@st.cache_data(ttl=300)  # 5分間キャッシュ
def fetch_traffic_flow(api_key, lat, lon, radius=5000):
    """HERE Traffic Flow APIから交通流量情報を取得"""
    base_url = "https://data.traffic.hereapi.com/v7/flow"
    
    params = {
        "apiKey": api_key,
        "in": f"circle:{lat},{lon};r={radius}",
        "locationReferencing": "shape",
    }
    
    response = requests.get(base_url, params=params, timeout=10)
    # ... GeoJSON形式に変換
```

**ポイント**:
- `@st.cache_data(ttl=300)`: APIコールを5分間キャッシュしてパフォーマンス向上
- `locationReferencing="shape"`: 道路の形状情報を取得
- `in` パラメータ: 検索範囲を指定（円形、半径5km）
- **エンドポイント**: `/v7/flow` を使用（交通流量データ）

### MapLibreでの表示

```python
# MapLibreマップの作成
map_options = MapOptions(
    style=Carto.POSITRON,
    center=(lon, lat),
    zoom=13,
)

m = Map(map_options)
m.add_control(NavigationControl())

# 交通流量レイヤー（渋滞係数に基づく色分け）
traffic_layer = Layer(
    type=LayerType.LINE,
    source=traffic_source,
    paint={
        "line-color": [
            "step",
            ["get", "jamFactor"],
            "#00aa00",  # 緑: jamFactor < 2.0 (軽い)
            2.0,
            "#ffaa00",  # 黄: 2.0 <= jamFactor < 6.0 (中程度)
            6.0,
            "#ff0000",  # 赤: jamFactor >= 6.0 (重大)
        ],
        "line-width": 6,
        "line-opacity": 0.8,
    },
)
```

**ポイント**:
- データ駆動スタイリング: `jamFactor`プロパティに基づいて色を変更
- `step` 式: 渋滞係数の閾値で段階的に色を変更
- LineStringジオメトリで道路セグメントを表示
- 透明度を調整して地図の視認性を維持

## 🎯 応用例

このチュートリアルを基に、以下のような拡張が可能です：

### 1. ルート案内との統合
```python
# HERE Routing APIと組み合わせ
route = get_route(origin, destination, avoid_traffic=True)
traffic_on_route = filter_flows_on_route(route, traffic_flows)
```

### 2. 時系列分析
```python
# 定期的にデータを収集して傾向分析
traffic_history = collect_traffic_over_time(location, days=7)
plot_congestion_patterns(traffic_history)
```

### 3. アラート機能
```python
# 重大な渋滞を検出したら通知
if any(flow['jamFactor'] > 8.0 for flow in traffic_flows):
    st.warning("⚠️ 重大な渋滞が検出されました！")
```

### 4. 複数地点の比較
```python
# 複数の主要地点の交通状況を比較
locations = ["東京駅", "新宿駅", "渋谷駅"]
traffic_comparison = compare_traffic_across_locations(locations)
```

## 📊 データ形式

### HERE Traffic Flow API レスポンス構造

```json
{
  "results": [
    {
      "location": {
        "shape": {
          "links": [
            {
              "points": [
                {"lat": 35.681, "lng": 139.767},
                {"lat": 35.682, "lng": 139.768}
              ],
              "functionalClass": 1
            }
          ]
        },
        "length": 1850
      },
      "currentFlow": {
        "speed": 13.9,
        "speedUncapped": 33.3,
        "freeFlow": 27.8,
        "jamFactor": 7.5,
        "confidence": 0.9,
        "traversability": "open"
      }
    }
  ]
}
```

**重要**: APIは速度をメートル/秒 (m/s) で返します。表示時には km/h に変換します。

### GeoJSON変換後

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[139.767, 35.681], [139.768, 35.682]]
      },
      "properties": {
        "speed": 50.0,
        "freeFlow": 100.0,
        "speedUncapped": 120.0,
        "speedPercentage": 50.0,
        "jamFactor": 7.5,
        "congestionLevel": "重大",
        "confidence": 0.9,
        "functionalClass": 1,
        "functionalClassName": "高速道路",
        "length": 1850
      }
    }
  ]
}
```

## 🔒 セキュリティのベストプラクティス

1. **APIキーの保護**
   - APIキーをコードに直接埋め込まない
   - Streamlit Secretsまたは環境変数を使用
   - `.streamlit/secrets.toml`を`.gitignore`に追加

2. **レート制限**
   - キャッシングを活用してAPI呼び出しを削減
   - 無料プランの制限内で使用

3. **エラーハンドリング**
   - APIエラーに対する適切なフォールバック
   - ユーザーフレンドリーなエラーメッセージ

## 🔗 参考リンク

### HERE Platform
- [HERE Traffic API Documentation](https://developer.here.com/documentation/traffic-api/dev_guide/index.html)
- [HERE Traffic Flow API Reference](https://developer.here.com/documentation/traffic-api/dev_guide/topics/resource-type-flow.html)
- [HERE Developer Portal](https://developer.here.com/)
- [HERE API Playground](https://developer.here.com/documentation/examples/rest/traffic/traffic-flow)

### MapLibre
- [MapLibre GL JS Documentation](https://maplibre.org/maplibre-gl-js-docs/api/)
- [MapLibre Python Bindings](https://github.com/eodaGmbH/py-maplibregl)
- [MapLibre Style Specification](https://maplibre.org/maplibre-style-spec/)

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Caching Guide](https://docs.streamlit.io/library/advanced-features/caching)
- [Streamlit Secrets Management](https://docs.streamlit.io/library/advanced-features/secrets-management)

## 💡 トラブルシューティング

### API呼び出しが失敗する
- APIキーが正しいか確認
- HERE Developer Portalでプロジェクトのステータスを確認
- レート制限に達していないか確認

### 地図が表示されない
- ブラウザのコンソールでエラーを確認
- MapLibreのバージョン互換性を確認
- GeoJSONデータの形式が正しいか確認

### パフォーマンスが遅い
- キャッシュのTTL（Time To Live）を調整
- 検索半径を小さくする
- 表示する道路セグメント数を制限

### データが表示されない
- 選択した地域に交通流量データがあるか確認
- APIレスポンスが正しく変換されているか確認
- デモモードで動作確認してから実際のAPIを試す

## 📈 次のステップ

このチュートリアルを完了したら、以下を試してみましょう：

1. **HERE Routing API**を追加して、交通状況を考慮したルート案内
2. **HERE Weather API**を統合して、気象条件と交通の相関を分析
3. **リアルタイム更新機能**を実装（Streamlitの自動更新機能を使用）
4. **交通予測モデル**を構築（過去データを使用）
5. **HERE Incidents API**を追加して、事故や工事情報も同時に表示
6. **モバイル対応**のレスポンシブデザイン

## 🎓 まとめ

このチュートリアルでは：
- ✅ HERE Traffic Flow APIの基本的な使用方法を学習
- ✅ MapLibreでのデータ可視化技術を習得
- ✅ Streamlitでのインタラクティブアプリケーション開発
- ✅ APIキャッシングとパフォーマンス最適化
- ✅ セキュリティのベストプラクティス

これらの知識を基に、より高度な交通流量可視化アプリケーションを開発できます！
