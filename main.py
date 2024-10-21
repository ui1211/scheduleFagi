import json
from datetime import datetime

import pandas as pd
import streamlit as st


class ScheduleApp:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.df = self.load_data_from_json()

    def create_initial_df(self):
        """初期化用の空のデータフレームを作成"""
        return pd.DataFrame(columns=["Date", "StartTime"])

    def load_data_from_json(self):
        """JSONファイルからデータを読み込む"""
        try:
            with open(self.json_file_path, "r") as file:
                data = json.load(file)
                return pd.DataFrame(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.create_initial_df()

    def save_data_to_json(self):
        """データフレームをJSONファイルに保存"""
        self.df["Date"] = self.df["Date"].astype(str)  # 日付を文字列に変換
        self.df["StartTime"] = self.df["StartTime"].astype(str)  # 開始時間を文字列に変換
        with open(self.json_file_path, "w") as file:
            json.dump(self.df.to_dict(orient="records"), file, indent=4)

    def add_new_row(self, new_date, start_time):
        """新しい日程の行を追加"""
        new_row = {"Date": new_date, "StartTime": start_time}
        for col in self.df.columns.difference(["Date", "StartTime"]):
            new_row[col] = "未定"
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

    def add_user(self, user_name, new_date, start_time):
        """新しいユーザーと日程を追加または更新"""
        if not self.df[(self.df["Date"] == new_date) & (self.df["StartTime"] == start_time)].empty:
            st.warning("この日程はすでに存在します。")
        else:
            self.add_new_row(new_date, start_time)

        if user_name not in self.df.columns:
            self.df[user_name] = "未定"

        self.df.loc[
            (self.df["Date"] == new_date) & (self.df["StartTime"] == start_time),
            user_name,
        ] = "未定"
        self.save_data_to_json()
        st.success("ユーザーと日程が追加されました！")

    def add_user_form(self):
        """ユーザーと日程の追加フォーム"""
        with st.sidebar:
            with st.form("add_user_form"):
                user_name = st.text_input("ユーザー名を入力してください")
                new_date = st.date_input("日付を追加してください")
                start_time = st.time_input("開始時間", step=3600)

                add_user = st.form_submit_button("ユーザーと日程を追加")
                if add_user and user_name:
                    self.add_user(user_name, new_date, start_time)

    def display_editable_dataframe(self):
        """データフレームの表示と編集"""
        if not self.df.empty:
            column_config = {
                user: st.column_config.SelectboxColumn(options=["△", "〇", "×"], label=user)
                for user in self.df.columns.difference(["Date", "StartTime"])
            }

            edited_df = st.data_editor(
                self.df,
                column_config=column_config,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
            )

            if not edited_df.equals(self.df):
                self.df = edited_df
                self.save_data_to_json()
                st.rerun()
        else:
            st.write("まだ日程が追加されていません。")


# アプリケーションのインスタンスを作成
app = ScheduleApp("data.json")

# アプリケーションのUIとロジックを実行
app.add_user_form()
app.display_editable_dataframe()
