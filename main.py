import json

import pandas as pd
import streamlit as st

# JSONファイルのパス
JSON_FILE_PATH = "data.json"


# データフレームの初期化
def create_initial_df():
    return pd.DataFrame(columns=["DateTime", "User", "Status"])


# JSONファイルからデータを読み込む関数
def load_data_from_json():
    try:
        with open(JSON_FILE_PATH, "r") as file:
            data = json.load(file)
            return pd.DataFrame(data)
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルが存在しない場合、またはJSONが壊れている場合は空のデータフレームを返す
        return create_initial_df()


# データをJSONファイルに書き込む関数
def save_data_to_json(df):
    # データフレーム内のTimestampをISOフォーマットの文字列に変換して保存
    df["DateTime"] = df["DateTime"].astype(str)
    with open(JSON_FILE_PATH, "w") as file:
        json.dump(df.to_dict(orient="records"), file, indent=4)


# Streamlitのアプリケーション
st.title("JSONと連携した日程調整アプリ")

# JSONファイルからデータを読み込む
df = load_data_from_json()

# データが空の場合、初期化
if df.empty:
    st.write("データがありません。新しいデータを追加してください。")

# ユーザーの追加フォーム
with st.sidebar:
    with st.form("add_user_form"):
        user_name = st.text_input("ユーザー名を入力してください")
        new_date = st.date_input("日付を追加してください")
        new_time = st.time_input("時間を追加してください")
        status = st.selectbox("ステータスを選択してください", ["△", "〇", "×"])
        add_user = st.form_submit_button("ユーザーと日程を追加")
        if add_user and user_name:
            new_datetime = pd.to_datetime(f"{new_date} {new_time}")
            new_row = {"DateTime": new_datetime, "User": user_name, "Status": status}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data_to_json(df)
            st.success("ユーザーと日程が追加されました。")

# JSONファイルを再読み込みして最新のデータを反映
df = load_data_from_json()

# 日時でソート
if not df.empty:
    df = df.sort_values(by="DateTime").reset_index(drop=True)

# データフレームをインタラクティブに編集できるようにする
if not df.empty:
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

    # 編集されたデータフレームを保存する
    if st.button("変更を保存"):
        save_data_to_json(edited_df)
        st.success("JSONファイルが更新されました！")
        # 最新の状態にするため、再度JSONを読み込み
        df = load_data_from_json()

    # 現在の状況を表示
    st.write("### 現在の状況")
    st.dataframe(df)

    # データのエクスポート機能
    st.download_button(
        label="結果をCSVとしてダウンロード",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="schedule.csv",
        mime="text/csv",
    )
else:
    st.write("まだ日程が追加されていません。")
