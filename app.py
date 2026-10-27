from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Campus Queue Predictor", page_icon="🏫")

DATA_FILE = Path(__file__).parent / "observations.csv"

st.title("🏫 Campus Smart Queue Predictor")
st.write("Choose a campus place, date, and time for a demo crowd estimate.")

place = st.selectbox("Campus place", ["Canteen", "Library"])
selected_date = st.date_input("Date", value=date.today())
selected_time = st.time_input("Time")
exam_period = st.checkbox("It is an exam period")

hour = selected_time.hour
weekday = selected_date.weekday() < 5

# Demo rules only; this is not a trained AI model.
if place == "Canteen":
    if 7 <= hour < 10 or 16 <= hour < 18:
        score = 1
    elif 12 <= hour < 14:
        score = 2
    else:
        score = 0
else:
    if 9 <= hour < 12 or 14 <= hour < 18:
        score = 2
    elif 12 <= hour < 14 or 18 <= hour < 20:
        score = 1
    else:
        score = 0

if weekday and score > 0:
    score += 1

if exam_period and place == "Library":
    score += 1

if score <= 1:
    prediction = "Low"
elif score == 2:
    prediction = "Moderate"
elif score == 3:
    prediction = "High"
else:
    prediction = "Very high"

st.subheader("Estimated crowd level")
st.metric("Prediction", prediction)
st.caption("This demo uses time-based rules, not a trained AI model.")

st.divider()
st.subheader("Record the actual crowd")

with st.form("observation_form", clear_on_submit=True):
    actual_place = st.selectbox(
        "Place observed",
        ["Canteen", "Library"],
        key="actual_place",
    )
    rating = st.slider(
        "Crowd rating (1 = nearly empty, 5 = extremely crowded)",
        min_value=1,
        max_value=5,
        value=3,
    )
    submitted = st.form_submit_button("Save observation")

if submitted:
    new_row = pd.DataFrame([{
        "Date": str(selected_date),
        "Time": selected_time.strftime("%H:%M"),
        "Place": actual_place,
        "Crowd rating": rating,
    }])

    if DATA_FILE.exists():
        old_data = pd.read_csv(DATA_FILE)
        observations = pd.concat([old_data, new_row], ignore_index=True)
    else:
        observations = new_row

    observations.to_csv(DATA_FILE, index=False)
    st.success("Observation saved.")
    st.rerun()

st.divider()
st.subheader("Collected observations")

if DATA_FILE.exists():
    observations = pd.read_csv(DATA_FILE)
    st.dataframe(observations, use_container_width=True, hide_index=True)

    averages = observations.groupby("Place")["Crowd rating"].mean().round(2)
    st.write("Average crowd rating by place")
    st.bar_chart(averages)
else:
    st.info("No observations yet. Record one above.")