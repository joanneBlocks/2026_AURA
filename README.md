# 2026_AURA
AURA (Attention Understanding &amp; Response AI) is an AI-powered focus monitor for digital learning. It tracks engagement signals during tutorials and detects when attention drops, enabling timely nudges that bring users back into focus.

A hackathon project idea created in Developer Camp - Manila 2026.
> **Hackathon Project:** Future of Work | Health & Human Potential  
> **Location:** Makati, Philippines (Live Event)

## 🎯 Focus Tracks
- **Future of Work:** Identifying natural talent and optimizing productivity.
- **Health & Human Potential:** Monitoring mental focus and preventing burnout.

## 🛠️ Tech Stack (The "Green Zone" Plan)
- **Language:** Python 3.9+
- **AI/Vision:** [MediaPipe](https://google.github.io/mediapipe/) (Face Mesh & Iris Tracking)
- **Input Analysis:** `pynput` (Keyboard cadence & burst monitoring)
- **UI/Dashboard:** [Streamlit](https://streamlit.io/) (Real-time data visualization)
- **Data Handling:** Supabase

## 📊 Core Logic (The "Flow" Formula)
The system calculates a **Focus Score** based on two primary data streams:
1. **Visual Attention (60%):** 
   - Iris tracking (Screen centeredness)
   - Head pose estimation (Distraction detection)
   - Blink rate (Cognitive load indicator)
2. **Interaction Cadence (40%):**
   - WPM (Words Per Minute)
   - Typing "Bursts" vs. long idle gaps
   - Consistency of input

## 🚀 Environment Setup (Pre-Hackathon)
To ensure a smooth start on Day 1, ensure the following are installed:

```bash
# 1. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install Core Dependencies
pip install mediapipe opencv-python streamlit pynput pandas numpy
```

## 📝 Roadmap & Deliverables
- [ ] Phase 1: Real-time Camera Feed + MediaPipe Face Mesh integration. Frontend Design Development.
- [ ] Phase 2: Background listener for typing cadence (WPM/Burst).
- [ ] Phase 3: Logic engine to calculate "Focus Score" over time. Personality-Based AI Character Development.
- [ ] Phase 4: Streamlit Dashboard with live gauges and "Career Path" recommendations.

## 🔒 Privacy Note
This project is designed with Privacy-by-Design. All camera processing happens locally on the user's machine. No video data is recorded or uploaded to the cloud.