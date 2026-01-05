import cv2

class CameraManager:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self._initialize_camera(camera_id)

    def _initialize_camera(self, camera_id):
        if self.cap is not None:
            self.cap.release()
            
        print(f"[INFO] Attempting to open camera {camera_id}...")
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW) # Use DSHOW on Windows for faster/better res switching
        
        if not self.cap.isOpened():
            # Fallback
            print(f"[WARNING] Camera {camera_id} failed. Trying 0...")
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.camera_id = 0
            
        if not self.cap.isOpened():
             print("[ERROR] No cameras found.")
             
        # Default to High Res attempt
        self.set_resolution(1920, 1080)

    def set_resolution(self, width, height):
        if not self.is_opened():
             return
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"[INFO] Resolution set to: {actual_w}x{actual_h}")

    def read_frame(self):
        if not self.is_opened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self.cap:
             self.cap.release()

    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()
