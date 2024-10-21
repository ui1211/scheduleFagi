import json

import pandas as pd
import streamlit as st


class ScheduleApp:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.df = self.load_data_from_json()

    def create_initial_df(self):
        """Initialize an empty dataframe."""
        return pd.DataFrame(columns=["Date", "StartTime"])

    def load_data_from_json(self):
        """Load data from JSON file."""
        try:
            with open(self.json_file_path, "r") as file:
                data = json.load(file)
                df = pd.DataFrame(data)
                if "Date" not in df.columns or "StartTime" not in df.columns:
                    return self.create_initial_df()
                return df
        except (FileNotFoundError, json.JSONDecodeError):
            return self.create_initial_df()

    def save_data_to_json(self):
        """Save the dataframe to a JSON file."""
        if "Date" in self.df.columns and "StartTime" in self.df.columns:
            self.df["Date"] = self.df["Date"].astype(str)
            self.df["StartTime"] = self.df["StartTime"].astype(str)
            with open(self.json_file_path, "w") as file:
                json.dump(self.df.to_dict(orient="records"), file, indent=4)

    def schedule_exists(self, new_date, start_time):
        """Check if the schedule already exists."""
        return not self.df[(self.df["Date"] == new_date) & (self.df["StartTime"] == start_time)].empty

    def add_new_row(self, new_date, start_time, user_name):
        """Add a new schedule row."""
        new_row = {"Date": new_date, "StartTime": start_time}
        for col in self.df.columns.difference(["Date", "StartTime"]):
            new_row[col] = "未定"  # Default status for other users
        new_row[user_name] = "未定"  # Set default status for the current user
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

    def add_schedule(self, new_date, start_time):
        """Add a new schedule for the current user."""
        user_name = st.session_state.get("user_name")
        if self.schedule_exists(new_date, start_time):
            st.warning("This schedule already exists.")
        else:
            self.add_new_row(new_date, start_time, user_name)
            self.save_data_to_json()
            st.success("Schedule added successfully!")

    def add_user(self, user_name):
        """Add a new user column if it doesn't already exist."""
        if user_name not in self.df.columns:
            self.df[user_name] = "未定"
            self.save_data_to_json()
            st.success(f"User '{user_name}' added!")

    def display_editable_dataframe(self):
        """Display and edit the dataframe."""
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
            st.write("No schedules added yet.")

    def main_screen(self):
        """Main application screen."""
        self.display_editable_dataframe()

    def add_schedule_form(self):
        """Form for adding a new schedule (in the sidebar)."""
        with st.sidebar:
            st.header("Add a New Schedule")
            with st.form("add_schedule_form"):
                new_date = st.date_input("Select a date")
                start_time = st.time_input("Select a start time")

                add_schedule = st.form_submit_button("Add Schedule")
                if add_schedule:
                    self.add_schedule(new_date, start_time)

    def run(self):
        """Run the application."""
        self.add_schedule_form()
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

        if not st.session_state.authenticated:
            self.user_auth_modal()
        else:
            self.main_screen()

    @st.dialog("Enter your username", width="small")
    def user_auth_modal(self):
        """Modal for user authentication."""
        user_name = st.text_input("Username")
        if st.button("Submit"):
            if user_name:
                st.session_state.user_name = user_name
                self.add_user(user_name)
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.warning("Please enter a username.")


# Instantiate and run the app
app = ScheduleApp("data.json")
app.run()
