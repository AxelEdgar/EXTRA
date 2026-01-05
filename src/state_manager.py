import cv2
import numpy as np

class StateManager:
    STATE_COLD = "COLD" # Setup/Reference mode
    STATE_HOT = "HOT"   # Active monitoring mode

    def __init__(self):
        self.state = self.STATE_COLD
        self.reference_frame = None
        self.reference_gray = None
        self.intrusions = 0
        self.last_intrusion_time = 0
        
        # Configurable parameters
        self.threshold = 25
        self.min_area = 500
        
        # Logic state
        # Logic state
        self.intrusion_active = False
        self.use_gpu = True # Hardware acceleration preference
        self.alarm_active = False # Tracks if visual alarm is currently triggering log
        
        # View/Quality settings
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.high_quality = False # Logic for Lanczos4 upscaling
        
        self.intrusion_start_time = 0 # For duration metrics

    def set_cold(self):
        """Resets to COLD state."""
        self.state = self.STATE_COLD
        self.reference_frame = None
        self.reference_gray = None
        self.intrusions = 0
        self.intrusion_active = False
        self.alarm_active = False
        print("[INFO] System set to COLD state.")

    def set_hot(self, frame):
        """Sets to HOT state and captures reference."""
        self.state = self.STATE_HOT
        self.reference_frame = frame.copy()
        self.reference_gray = self._preprocess(frame)
        self.intrusion_active = False
        self.alarm_active = False
        print("[INFO] System set to HOT state. Reference captured.")

    def is_hot(self):
        return self.state == self.STATE_HOT

    def _preprocess(self, frame):
        """Grayscale and Gaussian Blur."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (21, 21), 0)
        return blur

    def detect_changes(self, frame):
        """
        Returns a list of contours that differ from reference.
        Only runs if state is HOT.
        """
        if not self.is_hot() or self.reference_gray is None:
            return []

        current_gray = self._preprocess(frame)
        
        # Robustness: Handle Resolution Change (e.g., Zoom)
        if self.reference_gray.shape != current_gray.shape:
            # print(f"[WARN] Resolution changed. Recapturing reference.")
            self.reference_gray = current_gray
            self.reference_frame = frame.copy()
            return []
        
        # Absolute difference between reference and current
        frame_delta = cv2.absdiff(self.reference_gray, current_gray)
        
        # Threshold to get binary image
        _, thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)
        
        # Dilate to fill holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_contours = []
        for c in contours:
            if cv2.contourArea(c) > self.min_area:
                valid_contours.append(c)
                
        return valid_contours

    def update_intrusion_status(self, detected):
        """
        Updates intrusion count based on rising edge logic.
        detected (bool): True if intrusion is currently detected.
        """
        if detected and not self.intrusion_active:
             # Rising edge: New intrusion
             self.intrusions += 1
             self.intrusion_active = True
        elif not detected:
             # Falling edge: Intrusion cleared
             self.intrusion_active = False

    def increment_intrusion(self):
        # Deprecated in favor of update_intrusion_status
        pass
