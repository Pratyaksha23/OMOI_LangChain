import streamlit as st
from core.insights import generate_weekly_summary

st.title("Weekly Insights")

if st.button("Generate Weekly Summary"):
    with st.spinner("Reviewing your week..."):
        summary = generate_weekly_summary()
    st.write(summary)