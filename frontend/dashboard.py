import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from backend.db import supabase
from backend.telemetry_engine import TelemetryEngine
from backend.vision_engine import VisionEngine
from backend.state import state
from backend.voice_assistant import speak, listen

# -------------------------
# 1. PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AURA", layout="wide")

# -------------------------
# 2. BACKGROUND WORKER
# -------------------------
def background_worker(t_engine, v_engine):
    """
    Runs forever in a background thread.
    Only processes data when a session is active.
    """
    while True:
        try:
            # ✅ KEY FIX: Do nothing until user clicks "Start Focus Session"
            if not state.session_active:
                time.sleep(0.5)
                continue

            # --- GET TELEMETRY DATA ---
            telemetry_data = t_engine.get_metrics(window_seconds=5)
            state.wpm = telemetry_data["wpm"]

            # --- GET VISION DATA ---
            vision_data = v_engine.get_flow_metrics()

            if vision_data["face_detected"]:
                # Convert 0.0–1.0 to 0–100
                state.focus_score = vision_data["focus_score"] * 100
                state.is_distracted = vision_data.get("is_looking_away", False)
            else:
                # No face in frame — decay focus score
                state.focus_score = max(0, state.focus_score - 1)
                state.is_distracted = True

            # --- SMOOTH AVERAGE ---
            if state.avg_focus == 0:
                state.avg_focus = state.focus_score
            else:
                state.avg_focus = (state.avg_focus * 0.9) + (state.focus_score * 0.1)

            print(f"✅ WPM={state.wpm} | Focus={int(state.focus_score)} | Distracted={state.is_distracted}")

            time.sleep(0.1)

        except Exception as e:
            print(f"Worker Error: {e}")
            time.sleep(1)

# -------------------------
# 3. INITIALIZATION
# -------------------------
@st.cache_resource
def get_engines():
    """
    Creates and starts the engines ONCE.
    Returns the actual engine objects, not strings.
    """
    print("🚀 Starting Engines...")
    
    # 1. Initialize
    t_engine = TelemetryEngine()
    v_engine = VisionEngine()
        
    # 2. Worker thread runs forever but waits for session_active flag
    thread = threading.Thread(target=background_worker, args=(t_engine, v_engine), daemon=True)
    thread.start()
    
    return t_engine, v_engine

t_engine, v_engine = get_engines()

# -------------------------
# 4. AUTO-REFRESH (THE HEARTBEAT)
# -------------------------
# This forces the script to rerun every 1 second to fetch new data from 'state'
if 'last_run' not in st.session_state:
    st.session_state['last_run'] = time.time()

if time.time() - st.session_state['last_run'] > 1.0:
    st.session_state['last_run'] = time.time()
    st.rerun() # Reruns the script to update UI

# -------------------------
# 5. GET REAL DATA (NO MORE RANDOM)
# -------------------------
# We read directly from the Global State class
focus_score   = state.focus_score  if state.session_active else 0
wpm           = state.wpm          if state.session_active else 0
avg_focus     = int(state.avg_focus) if state.session_active else 0
# If focus drops below 50, the user is considered distracted
is_distracted = (focus_score < 50)  if state.session_active else False

# We don't have these in state yet, so we can keep them static or add them later
off_screen_time = 0 
group_engagement = 85 

# -------------------------
# COLORS & CSS
# -------------------------
MIDNIGHT = "#0B1A33"
AURORA = "#6D5EF6"
SKY = "#38BDF8"
MINT = "#34D399"
AMBER = "#F59E0B"

st.markdown(f"""
<style>
.stApp {{ background-color: {MIDNIGHT}; }}
h1,h2,h3,h4 {{ color: white; }}
</style>
""", unsafe_allow_html=True)

st.title("AURA Focus Control Center")

# -------------------------
# SUPABASE INTEGRATION
# -------------------------

# Only save to DB if focus score changes significantly or every X seconds
# For now, let's just read history for the graph
try:
    response = supabase.table("focus_logs").select("*").order("created_at", desc=False).limit(50).execute()
    history = response.data
except Exception as e:
    # st.error(f"Failed to fetch from DB: {e}") # Hide error to keep UI clean
    history = []

if history:
    timeline = pd.DataFrame(history)
    if "focus_score" in timeline.columns:
        timeline.rename(columns={"focus_score": "focus"}, inplace=True)
    if "focus" not in timeline.columns:
        timeline["focus"] = focus_score
else:
    timeline = pd.DataFrame({"focus": [focus_score]})

# -------------------------
# ANALYTICS LOGIC
# -------------------------
average_focus = int(timeline["focus"].mean()) if not timeline.empty else 0

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
# CONTROL CENTER UI
# -------------------------
col1,col2,col3 = st.columns([2,2,1])

with col1:
    st.plotly_chart(focus_gauge(focus_score), width="stretch")

with col2:
    st.subheader("Flow State")
    if not state.session_active:
        st.info("⏸️ No active session.\nClick **Start Focus Session** to begin.")
    elif focus_score > 80:
        st.success("🔥 Deep Focus")
    elif focus_score > 55:
        st.info("✅ Focused")
    else:
        st.warning("⚠️ Focus Dropping")

with col3:
    st.subheader("Session Controls")

    if not state.session_active:
        # ✅ START: Engines only start when this button is clicked
        if st.button("▶️ Start Focus Session", type="primary", use_container_width=True):
            t_engine.start()
            v_engine.start()
            state.session_active = True
            st.rerun()
    else:
        st.success("🟢 Session LIVE")
        # ✅ STOP: Engines stop and all metrics reset
        if st.button("⏹️ End Session", use_container_width=True):
            t_engine.stop()
            v_engine.stop()
            state.session_active = False
            state.focus_score  = 0
            state.wpm          = 0
            state.avg_focus    = 0
            state.is_distracted = False
            st.rerun()

# -------------------------
# METRICS & GRAPHS
# -------------------------
st.markdown("## Focus Analytics")
a,b,c,d,e,f = st.columns(6)
a.metric("Average Focus", average_focus)
b.metric("Current Focus", int(focus_score))
c.metric("WPM", wpm) # Changed from Distractions to WPM
d.metric("Distracted?", "YES" if is_distracted else "NO") # Changed logic
e.metric("Off-Screen", off_screen_time)
f.metric("Engagement", f"{group_engagement}%")

st.subheader("Focus Timeline")

# Build a live timeline list in session_state
if "focus_history" not in st.session_state:
    st.session_state.focus_history = []

if state.session_active:
    st.session_state.focus_history.append(int(focus_score))
    # Keep last 60 data points (60 seconds at 1s refresh)
    st.session_state.focus_history = st.session_state.focus_history[-60:]

timeline_data = st.session_state.focus_history if st.session_state.focus_history else [0]

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
    yaxis_title="Focus Score",
    yaxis=dict(range=[0, 100])
)
st.plotly_chart(fig_timeline, width="stretch")

st.subheader("Group Engagement Level")
st.progress(group_engagement/100)

# -------------------------
# VOICE ASSISTANT
# -------------------------
st.divider()
st.header("AI Voice Assistant")
col7,col8 = st.columns(2)

with col7:
    st.subheader("Speech to Text")
    if st.button("Start Listening"):
        # This now calls the function from backend/voice_assistant.py
        text = listen()
        st.success(text)

with col8:
    st.subheader("Text to Speech")
    text_input = st.text_input("Enter text")
    if st.button("Speak"):
        # This now calls the function from backend/voice_assistant.py
        speak(text_input)

time.sleep(1)
st.rerun()