"""Usage and feedback dashboard.   streamlit run dashboard/app.py"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DATABASE_URL  # noqa: E402

st.set_page_config(page_title="Farashi Dashboard", layout="wide")
st.title("Farashi usage dashboard")
con = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
df = pd.read_sql("SELECT i.*, u.language FROM interactions i JOIN users u ON u.id = i.user_id", con)
if df.empty:
    st.info("No interactions yet.")
    st.stop()
df["created_at"] = pd.to_datetime(df["created_at"])
c1, c2, c3, c4 = st.columns(4)
c1.metric("Questions", len(df))
c2.metric("Unique users", df["user_id"].nunique())
c3.metric("Helpful rate", f"{df['rating'].dropna().mean():.0%}" if df["rating"].notna().any() else "n/a")
c4.metric("Median latency (ms)", int(df["latency_ms"].median()))
st.subheader("Questions per day")
st.bar_chart(df.set_index("created_at").resample("D").size())
st.subheader("Language mix")
st.bar_chart(df["language"].value_counts())
st.subheader("Recent interactions")
st.dataframe(df[["created_at", "language", "input_type", "transcript", "answer", "rating"]].tail(50))
