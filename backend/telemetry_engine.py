import time
import threading
from pynput import keyboard, mouse
import numpy as np

class TelemetryEngine:
    """
    The Core Backend for AURA (Privacy-First).
    Tracks Input Cadence (Keyboard/Mouse) to detect 'Flow State'.
    """
    def __init__(self):
        self.active = False
        self.keystrokes = []   # Stores timestamps of key presses
        self.mouse_events = [] # Stores timestamps of mouse activity
        
        # We need a lock because pynput runs on a separate thread
        self.lock = threading.Lock()

        # Listeners
        self.kb_listener = keyboard.Listener(on_press=self._on_key_press)
        self.mouse_listener = mouse.Listener(on_move=self._on_mouse_move, on_click=self._on_mouse_click)

    def start(self):
        """Starts the background listeners."""
        print("🚀 Telemetry Engine Started...")
        self.active = True
        self.kb_listener.start()
        self.mouse_listener.start()

    def stop(self):
        """Stops the background listeners."""
        self.active = False
        self.kb_listener.stop()
        self.mouse_listener.stop()
        print("🛑 Telemetry Engine Stopped.")

    def _on_key_press(self, key):
        """Callback for key presses."""
        if self.active:
            with self.lock:
                self.keystrokes.append(time.time())

    def _on_mouse_move(self, x, y):
        """Callback for mouse movement."""
        if self.active:
            current_time = time.time()
            with self.lock:
                # Optimization: Only record mouse move if 0.1s has passed since last one
                # This prevents flooding the array with thousands of micro-movements
                if not self.mouse_events or (current_time - self.mouse_events[-1] > 0.1):
                    self.mouse_events.append(current_time)

    def _on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse clicks."""
        if self.active and pressed:
            with self.lock:
                self.mouse_events.append(time.time())

    def get_metrics(self, window_seconds=5):
        """
        Calculates the 'Flow Score' based on the last X seconds.
        Returns a dictionary of metrics.
        """
        now = time.time()
        cutoff = now - window_seconds

        with self.lock:
            # Filter events to only include the last X seconds
            # We keep the old list clean by removing outdated events
            self.keystrokes = [t for t in self.keystrokes if t > cutoff]
            self.mouse_events = [t for t in self.mouse_events if t > cutoff]
            
            recent_keys = len(self.keystrokes)
            recent_mouse = len(self.mouse_events)

        # 1. Calculate WPM (approximate: 5 chars = 1 word)
        # Formula: (Chars / 5) * (60 / window_seconds)
        wpm = (recent_keys / 5) * (60 / window_seconds)

        # 2. Calculate Interaction Density (Actions per second)
        total_actions = recent_keys + recent_mouse
        actions_per_sec = total_actions / window_seconds

        # 3. Determine "State" based on thresholds
        if actions_per_sec > 2.5:
            state = "🔥 High Flow"
        elif actions_per_sec > 0.5:
            state = "✅ Active"
        else:
            state = "💤 Idle"

        return {
            "wpm": round(wpm, 1),
            "actions_per_sec": round(actions_per_sec, 2),
            "state": state,
            "timestamp": now
        }