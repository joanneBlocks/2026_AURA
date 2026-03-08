import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import json

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="AURA",
    layout="wide"
)

# -------------------------
# COLORS
# -------------------------

MIDNIGHT = "#0B1A33"
AURORA = "#6D5EF6"
SKY = "#38BDF8"
MINT = "#34D399"
AMBER = "#F59E0B"

# -------------------------
# CSS
# -------------------------

st.markdown(f"""
<style>

.stApp {{
    background-color: {MIDNIGHT};
}}

h1,h2,h3,h4 {{
    color: white;
}}

</style>
""", unsafe_allow_html=True)

st.title("AURA Focus Control Center")

# -------------------------
# VOICE ENGINE
# -------------------------

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except:
        return "Focus, understood."

# -------------------------
# SIMULATED DATA
# -------------------------

focus_score = np.random.randint(40,100)

distraction_count = np.random.randint(0,10)
off_screen_time = np.random.randint(1,20)
group_engagement = np.random.randint(40,100)

# -------------------------
# FOCUS HISTORY
# -------------------------

try:
    with open("focus_log.json") as f:
        history = json.load(f)
except:
    history = []

history.append({
    "time": str(datetime.now()),
    "focus": focus_score
})

with open("focus_log.json","w") as f:
    json.dump(history,f)

timeline = pd.DataFrame(history)

# -------------------------
# ANALYTICS
# -------------------------

average_focus = int(timeline["focus"].mean())

# longest focus streak (focus > 70)
streak = 0
max_streak = 0

for value in timeline["focus"]:
    if value > 70:
        streak += 1
        max_streak = max(max_streak, streak)
    else:
        streak = 0

# -------------------------
# FOCUS GAUGE
# -------------------------

def focus_gauge(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Focus Level"},
        gauge={
            'axis': {'range':[0,100]},
            'bar':{'color':AURORA},
            'steps':[
                {'range':[0,50],'color':AMBER},
                {'range':[50,80],'color':SKY},
                {'range':[80,100],'color':MINT}
            ]
        }
    ))

    fig.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    return fig

# -------------------------
# CONTROL CENTER
# -------------------------

col1,col2,col3 = st.columns([2,2,1])

with col1:

    st.plotly_chart(
        focus_gauge(focus_score),
        use_container_width=True
    )

with col2:

    st.subheader("Flow State")

    if focus_score > 80:
        st.success("Deep Focus")

    elif focus_score > 55:
        st.info("Focused")

    else:
        st.warning("Focus Dropping")

with col3:

    st.subheader("Session Controls")

    if st.button("Start Focus Session"):
        st.success("Session Started")

    if st.button("End Session"):
        st.warning("Session Ended")

# -------------------------
# FOCUS ANALYTICS
# -------------------------

st.markdown("## Focus Analytics")

a,b,c,d,e,f = st.columns(6)

a.metric("Average Focus Score", average_focus)
b.metric("Current Focus", focus_score)
c.metric("Distractions", distraction_count)
d.metric("Longest Focus Streak", max_streak)
e.metric("Off-Screen Time (min)", off_screen_time)
f.metric("Group Engagement", f"{group_engagement}%")

# -------------------------
# FOCUS TIMELINE GRAPH
# -------------------------

st.subheader("Focus Timeline")

fig_timeline = go.Figure()

fig_timeline.add_trace(go.Scatter(
    y=timeline["focus"],
    mode="lines+markers",
    line=dict(color=SKY,width=3)
))

fig_timeline.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    xaxis_title="Session",
    yaxis_title="Focus Score"
)

st.plotly_chart(fig_timeline,use_container_width=True)

# -------------------------
# GROUP ENGAGEMENT BAR
# -------------------------

st.subheader("Group Engagement Level")

st.progress(group_engagement/100)

# -------------------------
# AI INSIGHTS
# -------------------------

st.markdown("## AI Insights")

if focus_score > 80:

    st.success("""
You are currently in **deep focus**.

Best tasks:\n
• coding\n
• analysis\n
• writing\n
""")

elif focus_score > 55:

    st.info("""
Focus is stable but not yet optimal.
Reducing distractions could improve productivity.
""")

else:

    st.warning("""
Focus level is dropping.
Consider taking a short break.
""")

# -------------------------
# VOICE ASSISTANT
# -------------------------

st.divider()

st.header("AI Voice Assistant")

col7,col8 = st.columns(2)

with col7:

    st.subheader("Speech to Text")

    if st.button("Start Listening"):

        text = listen()
        st.success(text)

with col8:

    st.subheader("Text to Speech")

    text_input = st.text_input("Enter text")

    if st.button("Speak"):
        speak(text_input)

# -------------------------
# ALERT
# -------------------------

if focus_score < 50:

    st.warning("Attention: Focus level dropping.")
    speak("Your focus level is dropping.")