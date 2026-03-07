import cv2
import mediapipe as mp
import math
import time

class VisionEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        # refine_landmarks=True is CRITICAL for Iris tracking
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True, 
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.is_running = False

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        print("👁️ Vision Engine Started...")

    def _calculate_distance(self, p1, p2):
        """Helper to get distance between two points"""
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _get_blink_ratio(self, landmarks, eye_indices):
        """Calculates Eye Aspect Ratio (EAR) to detect blinks"""
        # Horizontal line
        p1 = landmarks[eye_indices[0]] # Left corner
        p2 = landmarks[eye_indices[3]] # Right corner
        
        # Vertical lines
        p3 = landmarks[eye_indices[1]] # Top 1
        p4 = landmarks[eye_indices[5]] # Bottom 1
        p5 = landmarks[eye_indices[2]] # Top 2
        p6 = landmarks[eye_indices[4]] # Bottom 2

        horizontal = self._calculate_distance(p1, p2)
        vertical_1 = self._calculate_distance(p3, p4)
        vertical_2 = self._calculate_distance(p5, p6)

        if horizontal == 0: return 0
        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    def get_flow_metrics(self):
        success, image = self.cap.read()
        if not success:
            return {"focus_score": 0, "face_detected": False}

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # --- 1. HEAD POSE (Distraction Detection) ---
            # Compare Nose tip (1) to Left Ear (234) and Right Ear (454)
            nose = landmarks[1].x
            left_ear = landmarks[234].x
            right_ear = landmarks[454].x
            
            # Calculate ratio. 0.5 is perfectly center. 
            # < 0.3 or > 0.7 means looking away.
            face_width = right_ear - left_ear
            if face_width == 0: face_width = 0.001
            rel_nose_x = (nose - left_ear) / face_width
            
            is_looking_away = rel_nose_x < 0.3 or rel_nose_x > 0.7

            # --- 2. BLINK RATE (Cognitive Load) ---
            # Indices for Left Eye
            left_eye_indices = [33, 160, 158, 133, 153, 144]
            blink_ratio = self._get_blink_ratio(landmarks, left_eye_indices)
            
            # If ratio < 0.2, eye is closed
            is_blinking = blink_ratio < 0.2

            # --- 3. CALCULATE SCORE (Visual Attention) ---
            score = 100

            if is_looking_away:
                score -= 60  # Huge penalty for looking away
            elif is_blinking:
                score -= 10  # Small penalty for blinking (natural)
            
            # Normalize to 0.0 - 1.0
            final_score = max(0, score) / 100.0

            return {
                "focus_score": final_score, 
                "face_detected": True,
                "is_looking_away": is_looking_away,
                "is_blinking": is_blinking
            }
        
        return {"focus_score": 0, "face_detected": False}

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()