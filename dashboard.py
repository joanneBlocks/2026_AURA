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
CLOUD = "#E5E7EB"

# -------------------------
# CUSTOM CSS (DARK DASHBOARD)
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

# -------------------------
# TITLE
# -------------------------

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
        return "Could not understand audio"

# -------------------------
# SIMULATED DATA
# -------------------------

focus_score = np.random.randint(40,100)

health_data = {
    "Time": "34% ahead of schedule",
    "Tasks": "8 tasks to be completed",
    "Workload": "1 task overdue",
    "Progress": "58% complete",
    "Cost": "28% under budget"
}

task_data = pd.DataFrame({
    "Status": ["Not Started","Complete","In Progress"],
    "Count": [4,10,4]
})

progress_data = pd.DataFrame({
    "Category":[
        "Contracts",
        "Design",
        "Procurement",
        "Construction",
        "Post Construction",
        "Project Closing"
    ],
    "Progress":[100,95,100,8,38,0]
})

time_data = pd.DataFrame({
    "Type":["Planned Completion","Actual Completion","Ahead"],
    "Value":[24,58,34]
})

cost_data = pd.DataFrame({
    "Type":["Actual","Planned","Budget"],
    "Value":[180,200,250]
})

workload_data = pd.DataFrame({
    "Person":["Danny","Adam","Stephanie","Monica","John","Jennifer"],
    "Completed":[1,3,2,2,1,2],
    "Remaining":[2,2,2,1,0,0],
    "Overdue":[0,0,0,1,0,0]
})

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
# FOCUS GAUGE
# -------------------------

def focus_gauge(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Focus Level"},
        gauge={
            'axis': {'range': [0,100]},
            'bar': {'color': AURORA},
            'steps': [
                {'range': [0,50], 'color': AMBER},
                {'range': [50,80], 'color': SKY},
                {'range': [80,100], 'color': MINT}
            ]
        }
    ))

    fig.update_layout(
        height=320,

        # remove black background
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(color="white")
    )

    return fig

# -------------------------
# TOP CONTROL CENTER
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
# DASHBOARD ROW 1
# -------------------------

col4,col5,col6 = st.columns(3)

with col4:

    st.subheader("Health")

    for key,value in health_data.items():

        st.write(f"**{key}**")
        st.write(value)
        st.write("---")

with col5:

    st.subheader("Tasks")

    fig_tasks = go.Figure(data=[go.Pie(
        labels=task_data["Status"],
        values=task_data["Count"],
        hole=.65,
        marker=dict(colors=[SKY,MINT,AURORA])
    )])

    fig_tasks.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_tasks,use_container_width=True)

with col6:

    st.subheader("Progress")

    for i,row in progress_data.iterrows():

        st.write(row["Category"])
        st.progress(row["Progress"]/100)

# -------------------------
# DASHBOARD ROW 2
# -------------------------

col7,col8,col9 = st.columns(3)

with col7:

    st.subheader("Time")

    fig_time = go.Figure()

    fig_time.add_trace(go.Bar(
        y=time_data["Type"],
        x=time_data["Value"],
        orientation="h",
        marker_color=SKY
    ))

    fig_time.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_time,use_container_width=True)

with col8:

    st.subheader("Cost")

    fig_cost = go.Figure()

    fig_cost.add_trace(go.Bar(
        x=cost_data["Type"],
        y=cost_data["Value"],
        marker_color=AURORA
    ))

    fig_cost.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_cost,use_container_width=True)

with col9:

    st.subheader("Workload")

    fig_work = go.Figure()

    fig_work.add_trace(go.Bar(
        y=workload_data["Person"],
        x=workload_data["Completed"],
        name="Completed",
        orientation="h",
        marker_color=MINT
    ))

    fig_work.add_trace(go.Bar(
        y=workload_data["Person"],
        x=workload_data["Remaining"],
        name="Remaining",
        orientation="h",
        marker_color=SKY
    ))

    fig_work.add_trace(go.Bar(
        y=workload_data["Person"],
        x=workload_data["Overdue"],
        name="Overdue",
        orientation="h",
        marker_color=AMBER
    ))

    fig_work.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_work,use_container_width=True)

# -------------------------
# FOCUS TIMELINE
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
    font=dict(color="white")
)

st.plotly_chart(fig_timeline,use_container_width=True)

# -------------------------
# AI INSIGHTS
# -------------------------

st.markdown("## AI Insights")

if focus_score > 80:

    st.success("""
You are currently in **deep focus**.

Best time for:
• coding  
• analysis  
• writing
""")

elif focus_score > 55:

    st.info("""
You are focused but not in full flow state yet.
""")

else:

    st.warning("""
Your focus level is dropping.

Consider taking a break.
""")

# -------------------------
# VOICE ASSISTANT
# -------------------------

st.divider()

st.header("AI Voice Assistant")

col10,col11 = st.columns(2)

with col10:

    st.subheader("Speech to Text")

    if st.button("Start Listening"):

        text = listen()
        st.success(text)

with col11:

    st.subheader("Text to Speech")

    text_input = st.text_input("Enter text")

    if st.button("Speak"):
        speak(text_input)

# -------------------------
# ALERT
# -------------------------

if focus_score < 50:

    st.warning("Attention: Focus level dropping.")
    speak("Your focus level is dropping. Please refocus.")