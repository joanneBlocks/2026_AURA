# backend/state.py
import time

class GlobalState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalState, cls).__new__(cls)
            # Initialize default values
            cls._instance.focus_score = 0
            cls._instance.avg_focus = 0 
            cls._instance.wpm = 0
            cls._instance.actions_per_sec = 0
            cls._instance.is_distracted = False
            cls._instance.last_update = time.time()
            cls._instance.session_active = False
        return cls._instance

# Create a single instance to be imported
state = GlobalState()