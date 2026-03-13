import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force reload dashboard on every Streamlit rerun
import importlib
import frontend.dashboard as dashboard
importlib.reload(dashboard)