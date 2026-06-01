import sqlite3
import pandas as pd
import streamlit as st

# 画面を広く使う設定
st.set_page_config(layout="wide")

st.title("🎭 TheaterLog - 観劇記録 Webアプリ")

# データベースからデータを読み込む関数
def load_data():
    conn = sqlite3.connect("theater_log.db")
    query = "SELECT * FROM logs ORDER BY date DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# データベースに新しい記録を追加する関数
def insert_data(date, time, title, theater, seat, handler, memo):
    conn = sqlite3.connect("theater_log.db")
    cursor = conn.cursor()
    
    query = """
    INSERT INTO logs (date, time, title, theater, seat, handler, memo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (date, time, title, theater, seat, handler, memo))
    
    conn.commit()
    conn.close()

try:
    # ─── 左側（サイドバー）：新規入力フォーム ───
    with st.sidebar:
        st.header("➕ 新規観劇記録の追加")
        
        # 入力項目の作成
        input_date = st.date_input("公演日（必須）")
        input_time = st.text_input("時間（例: 13:00 / マチネ）", placeholder="13:00")
        input_title = st.text_input("作品名（必須）", placeholder="舞台 〇〇〇〇")
        input_theater = st.text_input("劇場", placeholder="〇〇劇場")
        input_seat = st.text_input("座席", placeholder="1階 12列 15番")
        input_handler = st.text_input("取扱", placeholder="FC先行 / チケプラ")
        input_memo = st.text_area("メモ", placeholder="感想やキャストなど")
        
        # 追加ボタン
        submit_button = st.button("データベースに追加する", use_container_width=True)
        
        if submit_button:
            # 必須入力のチェック
            if not input_title:
                st.error("作品名は必ず入力してください！")
            else:
                # 日付をテキスト形式（YYYY-MM-DD）に変換して保存
                date_str = input_date.strftime("%Y-%m-%d")
                
                # データベースに挿入
                insert_data(date_str, input_time, input_title, input_theater, input_seat, input_handler, input_memo)
                st.success(f"『{input_title}』を追加しました！")
                
                # データを再読み込みさせるために画面を強制リロード
                st.rerun()

    # ─── 右側（メイン画面）：データの表示と検索 ───
    raw_df = load_data()
    
    st.subheader("🔍 観劇記録を検索する")
    search_keyword = st.text_input("作品名、劇場、メモなどのキーワードを入力してください（空欄で全件表示）")
    
    if search_keyword:
        filtered_df = raw_df[
            raw_df['title'].str.contains(search_keyword, case=False, na=False) |
            raw_df['theater'].str.contains(search_keyword, case=False, na=False) |
            raw_df['memo'].str.contains(search_keyword, case=False, na=False) |
            raw_df['handler'].str.contains(search_keyword, case=False, na=False)
        ]
    else:
        filtered_df = raw_df

    st.metric(label="📊 該当本数", value=f"{len(filtered_df)} 本 / 全 {len(raw_df)} 本")
    
    st.subheader("🎬 観劇記録一覧")
    
    column_mapping = {
        "id": "ID",
        "date": "公演日",
        "time": "時間",
        "title": "作品名",
        "theater": "劇場",
        "seat": "座席",
        "handler": "取扱",
        "memo": "メモ"
    }
    
    display_df = filtered_df.rename(columns=column_mapping)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"エラーが発生しました: {e}")