import streamlit as st
import plotly.graph_objects as go

from core.emotion_analysis import analyze_emotion
from core.reflection import generate_reflection
from core.memory import add_entry, clear_memory
from utils.storage import save_entry, clear_entries, can_add_entry

st.title("Hi! I am Omoi!")

allowed, wait_message = can_add_entry()
journal = st.text_area("How was your day?", disabled=not allowed)

if not allowed:
    st.warning(wait_message)

def show_emotion_donut(emotion: dict):
    labels = list(emotion.keys())
    values = list(emotion.values())

    fig = go.Figure(data=[go.Pie(
        labels=[l.capitalize() for l in labels],
        values=values,
        hole=0.5,                          
        textinfo="none",
        marker=dict(line=dict(color="#ffffff", width=2))
    )])

    fig.update_layout(
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20),
        height=420
    )

    st.plotly_chart(fig, use_container_width=True)

if st.button("Analyze", disabled=not allowed):
    if not journal.strip():
        st.warning("Write something first.")
    else:
        with st.spinner("Thinking..."):
            emotion = analyze_emotion(journal)
            reflection = generate_reflection(journal, emotion)

        save_entry({
            "journal": journal,
            "emotion": emotion,
            "reflection": reflection
        })
        add_entry(journal)

        st.subheader("Emotion Breakdown")
        show_emotion_donut(emotion)

        st.subheader("Reflection")
        st.write(reflection["reflection"])

        st.subheader("Encouragement")
        st.write(reflection["encouragement"])

        st.subheader("Tomorrow")
        st.write(reflection["activity"])

st.divider()

if st.button("Reset Test Data"):
    clear_memory()
    clear_entries()
    st.success("All test data cleared!")
    st.rerun()