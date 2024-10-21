import pandas as pd
import streamlit as st


# 初期のデータフレームの作成関数
def create_initial_df():
    return pd.DataFrame(columns=["DateTime"])


# セッションステートにデータフレームを保存
if "df" not in st.session_state:
    st.session_state.df = create_initial_df()

if "users" not in st.session_state:
    st.session_state.users = []

st.title("日程調整")

with st.sidebar:

    # ユーザーの追加フォーム
    with st.form("add_user_form"):
        user_name = st.text_input("ユーザー名を入力してください")
        add_user = st.form_submit_button("ユーザーを追加")
        if add_user and user_name:
            if user_name not in st.session_state.users:
                st.session_state.users.append(user_name)
                st.session_state.df[user_name] = "未定"  # 新しいユーザー列を追加
            else:
                st.warning("このユーザーはすでに追加されています。")

    # 日程追加フォーム
    with st.form("add_date_form"):
        new_date = st.date_input("日付を追加してください")
        new_time = st.time_input("時間を追加してください")
        submitted = st.form_submit_button("日程を追加")
        if submitted:
            new_datetime = pd.to_datetime(f"{new_date} {new_time}")
            if new_datetime not in st.session_state.df["DateTime"].values:
                new_row = {"DateTime": new_datetime}
                for user in st.session_state.users:
                    new_row[user] = "未定"
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            else:
                st.warning("この日程はすでに追加されています。")

# 日時でソート
if not st.session_state.df.empty:
    st.session_state.df = st.session_state.df.sort_values(by="DateTime").reset_index(drop=True)

# データフレームをインタラクティブに編集できるようにする
if not st.session_state.df.empty:
    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            user: st.column_config.SelectboxColumn(options=["△", "〇", "×"], label=f"{user}のステータス")
            for user in st.session_state.users
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

    # 編集されたデータフレームをセッションステートに保存
    st.session_state.df = edited_df

    # 現在の状況を表示
    # st.write("### 現在の状況")
    # st.dataframe(st.session_state.df)

    # # データのエクスポート機能
    # st.download_button(
    #     label="結果をCSVとしてダウンロード",
    #     data=st.session_state.df.to_csv(index=False).encode("utf-8"),
    #     file_name="schedule.csv",
    #     mime="text/csv",
    # )
else:
    st.write("まだ日程が追加されていません。")
