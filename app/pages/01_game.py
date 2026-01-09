import json
import os
import random
import tempfile
from typing import Any, Dict

import pandas as pd
import pydeck as pdk
import streamlit as st

# ---- 設定 ----
STATS_FILE = "stats.json"  # 保存先（変更可）
NUM_QUESTIONS = 10

# 都道府県・県庁所在地・緯度経度（代表位置）
PREFECTURES = [
    ("北海道", "札幌市", 43.06417, 141.34694),
    ("青森県", "青森市", 40.82444, 140.74),
    ("岩手県", "盛岡市", 39.70361, 141.1525),
    ("宮城県", "仙台市", 38.26889, 140.87194),
    ("秋田県", "秋田市", 39.71861, 140.1025),
    ("山形県", "山形市", 38.24056, 140.36333),
    ("福島県", "福島市", 37.75, 140.46778),
    ("茨城県", "水戸市", 36.365, 140.47144),
    ("栃木県", "宇都宮市", 36.5551, 139.8828),
    ("群馬県", "前橋市", 36.39111, 139.06083),
    ("埼玉県", "さいたま市", 35.86166, 139.6455),
    ("千葉県", "千葉市", 35.60472, 140.12333),
    ("東京都", "新宿区", 35.69384, 139.70361),
    ("神奈川県", "横浜市", 35.4437, 139.638),
    ("新潟県", "新潟市", 37.91667, 139.03639),
    ("富山県", "富山市", 36.69528, 137.21139),
    ("石川県", "金沢市", 36.56111, 136.65622),
    ("福井県", "福井市", 36.06528, 136.22194),
    ("山梨県", "甲府市", 35.66444, 138.56833),
    ("長野県", "長野市", 36.65139, 138.18111),
    ("岐阜県", "岐阜市", 35.42333, 136.76056),
    ("静岡県", "静岡市", 34.97556, 138.38278),
    ("愛知県", "名古屋市", 35.18144, 136.9064),
    ("三重県", "津市", 34.72943, 136.5086),
    ("滋賀県", "大津市", 35.00444, 135.86833),
    ("京都府", "京都市", 35.02139, 135.75556),
    ("大阪府", "大阪市", 34.69374, 135.50218),
    ("兵庫県", "神戸市", 34.69139, 135.18306),
    ("奈良県", "奈良市", 34.68528, 135.80472),
    ("和歌山県", "和歌山市", 34.22583, 135.1675),
    ("鳥取県", "鳥取市", 35.50111, 134.235),
    ("島根県", "松江市", 35.46806, 133.05056),
    ("岡山県", "岡山市", 34.66167, 133.935),
    ("広島県", "広島市", 34.39639, 132.45944),
    ("山口県", "山口市", 34.18583, 131.47139),
    ("徳島県", "徳島市", 34.07028, 134.55444),
    ("香川県", "高松市", 34.34278, 134.04639),
    ("愛媛県", "松山市", 33.83944, 132.76556),
    ("高知県", "高知市", 33.55972, 133.53111),
    ("福岡県", "福岡市", 33.60639, 130.41806),
    ("佐賀県", "佐賀市", 33.24944, 130.29889),
    ("長崎県", "長崎市", 32.75028, 129.87778),
    ("熊本県", "熊本市", 32.80306, 130.70778),
    ("大分県", "大分市", 33.23806, 131.6125),
    ("宮崎県", "宮崎市", 31.91111, 131.42389),
    ("鹿児島県", "鹿児島市", 31.59306, 130.55778),
    ("沖縄県", "那覇市", 26.2125, 127.68111),
]

# 辞書マップ（lookup 用）
PREF_BY_PREF = {p: (c, la, lo) for (p, c, la, lo) in PREFECTURES}
PREF_BY_CAP = {c: (p, la, lo) for (p, c, la, lo) in PREFECTURES}


# ---- ファイル I/O / 統計関連 ----
def load_global_stats(path: str = STATS_FILE) -> Dict[str, Any]:
    """stats.json を読み込んで dict を返す。ファイルがなければ空の dict。"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except Exception:
        return {}


def atomic_write_json(path: str, data: Dict[str, Any]):
    """一時ファイルに書いてから os.replace で原子上書き（簡易実装）。"""
    dirpath = os.path.dirname(os.path.abspath(path)) or "."
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=dirpath, delete=False
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp_name = tmp.name
    os.replace(tmp_name, path)


def save_global_stats(stats: Dict[str, Any], path: str = STATS_FILE):
    """global 統計を保存。競合対策が必要なら filelock を使う等拡張。"""
    atomic_write_json(path, stats)


def merge_session_into_global(
    session_answered, global_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    session_answered: list of entries (user_answer, correct_answer, is_correct, pref, cap, lat, lon)
    global_stats format (per-pref keyed by prefecture name):
    {
        "<都道府県>": {"pref": "<>", "cap": "<>", "lat": <>, "lon": <>, "attempts": n, "corrects": m}
    }
    """
    out = dict(global_stats)  # shallow copy
    for entry in session_answered:
        if not entry:
            continue
        # entry: user_answer, correct_answer, is_correct, pref, cap, lat, lon
        user_ans, correct_ans, is_correct, pref, cap, lat, lon = entry
        key = pref
        rec = out.get(
            key,
            {
                "pref": pref,
                "cap": cap,
                "lat": lat,
                "lon": lon,
                "attempts": 0,
                "corrects": 0,
            },
        )
        rec["attempts"] = rec.get("attempts", 0) + 1
        rec["corrects"] = rec.get("corrects", 0) + (1 if is_correct else 0)
        # keep lat/lon/cap consistent if missing
        rec.setdefault("lat", lat)
        rec.setdefault("lon", lon)
        rec.setdefault("cap", cap)
        out[key] = rec
    return out


# ---- 正規化などユーティリティ ----
def normalize_name(name: str) -> str:
    if name is None:
        return ""
    s = name.strip()
    s = s.replace("　", "").replace(" ", "")
    s = s.lower()
    for suf in ("県", "都", "府", "道"):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s


def generate_mc_options_for_sample(sample):
    capitals = [cap for (_pref, cap, _lat, _lon) in PREFECTURES]
    mc_options = []
    for pref, cap, _lat, _lon in sample:
        wrongs = random.sample([c for c in capitals if c != cap], k=3)
        opts = wrongs + [cap]
        random.shuffle(opts)
        mc_options.append(opts)
    return mc_options


# ---- アプリ本体のロジック ----
def start_quiz():
    mode = st.session_state.get("selected_mode", "capital_to_pref_input")
    sample = random.sample(PREFECTURES, k=NUM_QUESTIONS)
    st.session_state.quiz = sample
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.answered = [
        None
    ] * NUM_QUESTIONS  # (user_answer, correct_answer, is_correct, pref, cap, lat, lon)
    st.session_state.show_answer = False
    st.session_state.mode = mode
    st.session_state.answer_input = ""
    if mode in ("pref_to_capital_mc", "map_capital_mc"):
        st.session_state.mc_options = generate_mc_options_for_sample(sample)


def submit_answer_callback():
    idx = st.session_state.index
    mode = st.session_state.get("mode", "capital_to_pref_input")
    pref, cap, lat, lon = st.session_state.quiz[idx]
    if mode == "capital_to_pref_input":
        user_input = st.session_state.get("answer_input", "")
        is_correct = (
            normalize_name(user_input) == normalize_name(pref)
            and normalize_name(user_input) != ""
        )
        if is_correct:
            st.session_state.score += 1
        st.session_state.answered[idx] = (
            user_input,
            pref,
            is_correct,
            pref,
            cap,
            lat,
            lon,
        )
    elif mode == "pref_to_capital_mc":
        key = f"mc_choice_{idx}"
        user_choice = st.session_state.get(key, "")
        is_correct = user_choice == cap
        if is_correct:
            st.session_state.score += 1
        st.session_state.answered[idx] = (
            user_choice,
            cap,
            is_correct,
            pref,
            cap,
            lat,
            lon,
        )
    else:  # map_capital_mc
        key = f"mc_choice_{idx}"
        user_choice = st.session_state.get(key, "")
        is_correct = user_choice == pref
        if is_correct:
            st.session_state.score += 1
        st.session_state.answered[idx] = (
            user_choice,
            pref,
            is_correct,
            pref,
            cap,
            lat,
            lon,
        )
    st.session_state.show_answer = True


def show_hint_callback():
    idx = st.session_state.index
    mode = st.session_state.get("mode", "capital_to_pref_input")
    pref, cap, lat, lon = st.session_state.quiz[idx]
    if mode == "capital_to_pref_input":
        st.session_state.answered[idx] = (
            st.session_state.get("answer_input", ""),
            pref,
            False,
            pref,
            cap,
            lat,
            lon,
        )
    else:
        key = f"mc_choice_{idx}"
        st.session_state.answered[idx] = (
            st.session_state.get(key, "") or "",
            cap if mode == "pref_to_capital_mc" else pref,
            False,
            pref,
            cap,
            lat,
            lon,
        )
    st.session_state.show_answer = True


def next_question_callback():
    prev_idx = st.session_state.index
    st.session_state.index += 1
    st.session_state.show_answer = False
    mc_key = f"mc_choice_{prev_idx}"
    if mc_key in st.session_state:
        st.session_state[mc_key] = None
    st.session_state.answer_input = ""


def reset_to_start_callback():
    for k in [
        "quiz",
        "index",
        "score",
        "answered",
        "show_answer",
        "mode",
        "mc_options",
        "answer_input",
    ]:
        if k in st.session_state:
            del st.session_state[k]


def restart_quiz_callback():
    start_quiz()


# ---- UI ----
st.title("都道府県あてゲーム（累積統計をJSONで保存）")
st.write("モードを選んで「ゲームをスタート」を押してください。")

if "quiz" not in st.session_state:
    default_mode = st.session_state.get("selected_mode", "capital_to_pref_input")
    st.radio(
        "出題モード",
        options=["capital_to_pref_input", "pref_to_capital_mc", "map_capital_mc"],
        format_func=lambda x: {
            "capital_to_pref_input": "県庁所在地（市名）を見て都道府県を当てる（入力式）",
            "pref_to_capital_mc": "都道府県名を見て県庁所在地を選ぶ（4択）",
            "map_capital_mc": "地図上に県庁所在地を表示 → 都道府県を選ぶ（4択・pydeck）",
        }[x],
        key="selected_mode",
        index=["capital_to_pref_input", "pref_to_capital_mc", "map_capital_mc"].index(
            default_mode
        ),
    )
    cols = st.columns([1, 1])
    with cols[0]:
        st.button("ゲームをスタート", on_click=start_quiz)
    with cols[1]:
        st.button("サンプル実行（同じモードで即スタート）", on_click=start_quiz)
    st.write("---")
    st.info("モードを選択してから「ゲームをスタート」を押してください。")
    st.stop()

# ゲーム中
quiz = st.session_state.quiz
idx = st.session_state.index
score = st.session_state.score
answered = st.session_state.answered
show_answer = st.session_state.show_answer
mode = st.session_state.get("mode", "capital_to_pref_input")

# 終了画面
if idx >= NUM_QUESTIONS:
    st.subheader("結果")
    st.write(f"正解数: {st.session_state.score} / {NUM_QUESTIONS}")
    st.write("---")

    # 1) セッション内統計（テーブル）
    stats = {}
    for entry in answered:
        if entry is None:
            continue
        user_ans, correct_ans, is_correct, pref, cap, lat, lon = entry
        s = stats.setdefault(
            pref,
            {
                "pref": pref,
                "cap": cap,
                "lat": lat,
                "lon": lon,
                "attempts": 0,
                "corrects": 0,
            },
        )
        s["attempts"] += 1
        if is_correct:
            s["corrects"] += 1
    rows = []
    for v in stats.values():
        attempts = v["attempts"]
        corrects = v["corrects"]
        rate = corrects / attempts if attempts > 0 else None
        rows.append(
            {
                "都道府県": v["pref"],
                "県庁所在地": v["cap"],
                "試行回数": attempts,
                "正解数": corrects,
                "正答率": round(rate, 3) if rate is not None else None,
                "lat": v["lat"],
                "lon": v["lon"],
            }
        )
    if rows:
        df_session = pd.DataFrame(rows).sort_values("正答率")
        st.subheader("今回セッションの都道府県ごとの正答率")
        st.dataframe(
            df_session[
                ["都道府県", "県庁所在地", "試行回数", "正解数", "正答率"]
            ].reset_index(drop=True)
        )
    else:
        st.info("今回のセッションには統計データがありません。")

    # 2) 累積（global）統計の読み込み→今回セッションをマージして保存
    global_stats = load_global_stats()
    merged = merge_session_into_global(answered, global_stats)
    try:
        save_global_stats(merged)
        st.success(f"累積統計を {STATS_FILE} に保存しました。")
    except Exception as e:
        st.error(f"統計の保存に失敗しました: {e}")

    # 3) 累積統計の表示（読み込み直して表示）
    global_stats_after = load_global_stats()
    if global_stats_after:
        rows_g = []
        for v in global_stats_after.values():
            attempts = v.get("attempts", 0)
            corrects = v.get("corrects", 0)
            rate = corrects / attempts if attempts > 0 else None
            rows_g.append(
                {
                    "都道府県": v.get("pref"),
                    "県庁所在地": v.get("cap"),
                    "試行回数": attempts,
                    "正解数": corrects,
                    "正答率": round(rate, 3) if rate is not None else None,
                    "lat": v.get("lat"),
                    "lon": v.get("lon"),
                }
            )
        df_global = pd.DataFrame(rows_g).sort_values("正答率")
        st.subheader("累積（全セッション）都道府県ごとの正答率")
        st.dataframe(
            df_global[
                ["都道府県", "県庁所在地", "試行回数", "正解数", "正答率"]
            ].reset_index(drop=True)
        )

        # 間違えヒートマップ（累積）： weight = 間違い回数
        heat_data = []
        for r in rows_g:
            wrongs = r["試行回数"] - r["正解数"]
            if wrongs > 0:
                heat_data.append(
                    {
                        "lat": r["lat"],
                        "lon": r["lon"],
                        "weight": wrongs,
                        "cap": r["県庁所在地"],
                        "pref": r["都道府県"],
                    }
                )
        if heat_data:
            st.subheader("累積 間違いヒートマップ（pydeck）")
            layer = pdk.Layer(
                "HeatmapLayer",
                data=heat_data,
                get_position=["lon", "lat"],
                get_weight="weight",
                radiusPixels=50,
            )
            view_state = pdk.ViewState(
                latitude=36.0, longitude=138.0, zoom=4.5, pitch=0
            )
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{pref}\n{cap}\n{weight} 間違い"},  # type: ignore
            )
            st.pydeck_chart(deck)
    else:
        st.info("累積統計が存在しません（まだ保存されていません）。")

    st.write("---")
    cols = st.columns([1, 1, 1])
    with cols[0]:
        st.button("もう一度（同モードで再開）", on_click=restart_quiz_callback)
    with cols[1]:
        st.button("スタート画面に戻る（モード選択）", on_click=reset_to_start_callback)
    with cols[2]:
        # もう一度プレイか、セッションを完全にクリアしてスタート画面へ
        st.button("セッションを初期化して最初から", on_click=reset_to_start_callback)
    st.stop()

# 現在の問題表示
item = quiz[idx]
# 柔軟な unpack（古いセッションフォーマット対応）
if isinstance(item, (list, tuple)):
    if len(item) >= 4:
        pref, cap, lat, lon = item[0], item[1], item[2], item[3]
    elif len(item) == 2:
        pref, cap = item
        if pref in PREF_BY_PREF:
            _cap, lat, lon = PREF_BY_PREF[pref]
        elif cap in PREF_BY_CAP:
            pref, lat, lon = (
                PREF_BY_CAP[cap][0],
                PREF_BY_CAP[cap][1],
                PREF_BY_CAP[cap][2],
            )
        else:
            lat, lon = 36.0, 138.0
    else:
        pref, cap, lat, lon = "不明", "不明", 36.0, 138.0
else:
    pref, cap, lat, lon = "不明", "不明", 36.0, 138.0

st.markdown(f"### 問題 {idx + 1} / {NUM_QUESTIONS}")

if mode == "capital_to_pref_input":
    st.write(f"県庁所在地: **{cap}**")
    st.text_input(
        "都道府県名を入力してください（例：大阪府 または 大阪）",
        key="answer_input",
        placeholder="例：千葉県、東京、沖縄",
    )
elif mode == "pref_to_capital_mc":
    st.write(f"都道府県: **{pref}**")
    options = st.session_state.get("mc_options", generate_mc_options_for_sample(quiz))
    choice_key = f"mc_choice_{idx}"
    st.radio("県庁所在地（4択）を選んでください", options=options[idx], key=choice_key)
else:  # map_capital_mc
    st.write(
        "地図上に表示された地点（県庁所在地）を見て、正しい都道府県を選んでください。"
    )
    map_data = pd.DataFrame([{"lat": lat, "lon": lon, "name": cap}])
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position=["lon", "lat"],
        get_radius=5000,
        get_fill_color=[255, 0, 0],
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=7, pitch=0)
    deck = pdk.Deck(
        layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}"}  # type: ignore
    )
    st.pydeck_chart(deck)
    # 選択肢は都道府県名（pref）を混ぜる（ランダム生成）
    pref_lists = [p for (p, c, la, lo) in PREFECTURES]
    wrongs = random.sample([p for p in pref_lists if p != pref], k=3)
    opts = wrongs + [pref]
    random.shuffle(opts)
    choice_key = f"mc_choice_{idx}"
    st.radio("都道府県（4択）を選んでください", options=opts, key=choice_key)

# 操作ボタン
cols = st.columns([1, 1, 1])
with cols[0]:
    if not show_answer:
        st.button("回答する", on_click=submit_answer_callback)
with cols[1]:
    if not show_answer:
        st.button("答えを見る（ヒント）", on_click=show_hint_callback)
with cols[2]:
    if show_answer:
        st.button("次へ", on_click=next_question_callback)

# 回答表示
if show_answer:
    user_ans, correct_ans, is_correct, _pref, _cap, _lat, _lon = (
        st.session_state.answered[idx]
    )
    user_display = user_ans if user_ans else "（未回答）"
    if is_correct:
        st.success(f"正解！ 正解は **{correct_ans}** です。あなた: {user_display}")
    else:
        st.error(f"不正解。正解は **{correct_ans}** です。あなた: {user_display}")
    st.write(f"現在の正解数: **{st.session_state.score} / {idx + 1}**")
else:
    st.info("入力／選択して「回答する」を押してください。")

# フッター：進捗とリスタート
st.write("---")
st.write(f"進捗: {idx} / {NUM_QUESTIONS} (正解: {st.session_state.score})")
st.button("リセットして最初から（スタート画面へ）", on_click=reset_to_start_callback)
