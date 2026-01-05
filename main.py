import cv2
import numpy as np
from src.camera_manager import CameraManager
from src.zone_manager import ZoneManager
from src.state_manager import StateManager
from src.ui_renderer import UIRenderer
from src.log_manager import LogManager
import time

# Global references
current_hitboxes = []
actions_queue = []
renderer = None
zone_manager = None
log_manager = None

# Global Application State for Coordinate Mapping
class AppState:
    def __init__(self):
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.img_w = 640
        self.img_h = 480
        # Panning State
        self.is_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        # Modes
        self.is_hand_mode = False # True = Pan/Hand, False = Draw/Zone

app_state = AppState()

def mouse_callback(event, x, y, flags, param):
    global current_hitboxes, actions_queue, app_state, zone_manager, renderer
    
    # --- DRAGGING LOGIC (PANNING) ---
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check GUI Hitboxes first
        action_triggered = False
        for hb in current_hitboxes:
            rx1, ry1, rx2, ry2 = hb['rect']
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                # Capture Action
                if 'params' in hb:
                    actions_queue.append({'action': hb['action'], 'params': hb['params'], 'click_x': x})
                else:
                    actions_queue.append({'action': hb['action']})
                action_triggered = True
                break
        
        # If not UI, check Video Area
        if not action_triggered and renderer is not None and hasattr(renderer, 'current_video_area'):
            vx, vy, vw, vh = renderer.current_video_area
            if vx <= x <= vx + vw and vy <= y <= vy + vh:
                
                # --- MODE CHECK ---
                if app_state.is_hand_mode:
                    # PANNING MODE
                    app_state.is_dragging = True
                    app_state.last_mouse_x = x
                    app_state.last_mouse_y = y
                else:
                    # DRAWING MODE
                    # Transform logic (Keep existing Point logic)
                    rel_x = x - vx
                    rel_y = y - vy
                    crop_w = int(app_state.img_w / app_state.zoom_level)
                    crop_h = int(app_state.img_h / app_state.zoom_level)
                    scale_x = vw / crop_w
                    scale_y = vh / crop_h
                    crop_click_x = rel_x / scale_x
                    crop_click_y = rel_y / scale_y
                    final_x = int(crop_click_x + app_state.offset_x)
                    final_y = int(crop_click_y + app_state.offset_y)
                    final_x = max(0, min(app_state.img_w - 1, final_x))
                    final_y = max(0, min(app_state.img_h - 1, final_y))
                    
                    if zone_manager:
                        zone_manager.add_point(final_x, final_y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if app_state.is_dragging and app_state.is_hand_mode:
            # Panning
            dx = x - app_state.last_mouse_x
            dy = y - app_state.last_mouse_y
            
            if renderer and hasattr(renderer, 'current_video_area'):
                 vx, vy, vw, vh = renderer.current_video_area
                 # Scale factor
                 crop_w = int(app_state.img_w / app_state.zoom_level)
                 scale_x = crop_w / vw if vw > 0 else 1.0
                 
                 shift_x = int(dx * scale_x)
                 shift_y = int(dy * scale_x) # Assume uniform aspect roughly
                 
                 # Apply Inverted (Drag Image)
                 app_state.offset_x -= shift_x
                 app_state.offset_y -= shift_y
                 
                 app_state.last_mouse_x = x
                 app_state.last_mouse_y = y

    elif event == cv2.EVENT_LBUTTONUP:
        app_state.is_dragging = False

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Allow closing zone even in hand mode? Probably convenience.
        if zone_manager:
            if zone_manager.close_zone():
                 if log_manager: log_manager.add_log("INFO", "Zona Definida y Cerrada")
            else:
                 zone_manager.clear_current_zone()
                 if log_manager: log_manager.add_log("INFO", "Cancelado trazado de zona")

def main():
    global renderer, zone_manager, log_manager, current_hitboxes, actions_queue, app_state
    
    # Initialize Configuration
    camera = CameraManager(0)
    zone_manager = ZoneManager()
    state_manager = StateManager()
    renderer = UIRenderer()
    log_manager = LogManager()
    
    # Dashboard Canvas (Fixed Resolution)
    CANVAS_W = 1270
    CANVAS_H = 720
    canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
    
    window_name = "Sistema de Seguridad Visual Industrial"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    log_manager.add_log("INFO", "Dashboard HMI Inicializado Correctamente.")
    log_manager.add_log("INFO", "[ESPACIO] Alternar Mano/Dibujo")

    loop_counter = 0
    avg_fps = 0
    last_intrusion_count = 0

    while True:
        start_time = time.time()
        
        # 1. Read Frame (Robust)
        frame = camera.read_frame()
        
        if frame is None:
            # Create a black frame to keep UI alive
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "SIN SEÑAL DE VIDEO", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Try to reconnect every ~2s (assuming 30fps = 60 frames)
            if loop_counter % 60 == 0:
                 print("[INFO] Intentando reconectar cámara...")
                 camera.release()
                 try:
                    camera = CameraManager(camera.camera_id)
                 except: pass
        
        # Update State
        h, w = frame.shape[:2]
        app_state.img_w = w
        app_state.img_h = h
        
        # 2. Digital Zoom & Crop
        # Ensure zoom level is valid
        if app_state.zoom_level < 1.0: app_state.zoom_level = 1.0
        
        new_w = int(w / app_state.zoom_level)
        new_h = int(h / app_state.zoom_level)
        
        # --- PANNING CLAMP LOGIC ---
        max_offset_x = w - new_w
        max_offset_y = h - new_h
        
        app_state.offset_x = max(0, min(max_offset_x, app_state.offset_x))
        app_state.offset_y = max(0, min(max_offset_y, app_state.offset_y))
        
        cropped_frame = frame[app_state.offset_y:app_state.offset_y+new_h, 
                              app_state.offset_x:app_state.offset_x+new_w]
                              
        display_frame = cropped_frame.copy()

        # 3. Processing (if Hot)
        if state_manager.is_hot():
            contours = state_manager.detect_changes(display_frame)
            renderer.draw_detections(display_frame, contours)
            
            intrusion_detected = False
            for c in contours:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    dx = int(M["m10"] / M["m00"])
                    dy = int(M["m01"] / M["m00"])
                    
                    # Convert 'dx, dy' (Crop Space) to Camera Space for Zone Check
                    rx = int(dx + app_state.offset_x)
                    ry = int(dy + app_state.offset_y)
                    
                    if zone_manager.check_intersection((rx, ry)):
                        intrusion_detected = True
                        cv2.circle(display_frame, (dx, dy), 10, (0, 0, 255), -1)
                        
            state_manager.update_intrusion_status(intrusion_detected)
            if intrusion_detected:
                 renderer.trigger_visual_alarm(canvas)
                 # Log on rising edge only (when count increases)
                 if state_manager.intrusions > last_intrusion_count:
                     log_manager.add_log("ALARMA", f"Intrusión Detectada! (Nivel {state_manager.intrusions})")
                     last_intrusion_count = state_manager.intrusions

        # Sync local counter if reset
        if state_manager.intrusions < last_intrusion_count:
             last_intrusion_count = state_manager.intrusions


        # 4. Render Zones (On Video Frame)
        renderer.draw_zones_on_video(display_frame, zone_manager, app_state)

        # 5. Render Main Dashboard
        # Calculate Metrics (Smoothed FPS)
        elapsed = time.time() - start_time
        current_fps = 1.0 / elapsed if elapsed > 0 else 0
        
        # Simple Exponential Moving Average
        if avg_fps == 0: avg_fps = current_fps
        else: avg_fps = 0.95 * avg_fps + 0.05 * current_fps
        
        process_time_ms = elapsed * 1000
        
        metrics = {
            'fps': avg_fps,
            'latency': process_time_ms,
            'proc': 'GPU (OpenCL)' if state_manager.use_gpu else 'CPU'
        }
        
        # !!! RENDER CALL !!!
        # This updates 'current_hitboxes' implicitly for next frame since we return it
        current_hitboxes = renderer.render(canvas, display_frame, state_manager, log_manager, metrics)
        
        # --- DRAW CURRENT MODE OVERLAY ---
        mode_text = "[MANO - PANNING]" if app_state.is_hand_mode else "[DIBUJO ZONAS]"
        mode_color = (0, 255, 255) if app_state.is_hand_mode else (255, 100, 200)
        cv2.putText(canvas, mode_text, (20, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
        cv2.putText(canvas, "Presiona ESPACIO para cambiar", (20, 705), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # 6. Handle Interaction Queue
        max_actions_per_frame = 5
        processed_actions = 0
        while actions_queue and processed_actions < max_actions_per_frame:
            act_data = actions_queue.pop(0)
            act = act_data['action']
            processed_actions += 1
            
            if act == 'SET_COLD': 
                state_manager.set_cold()
                log_manager.add_log("INFO", "Sistema en modo COLD")
            elif act == 'SET_HOT': 
                # BUG FIX: Use cropped_frame (Clean) instead of display_frame (Painted)
                state_manager.set_hot(cropped_frame)
                log_manager.add_log("INFO", "Sistema ARMADO (HOT)")
            elif act == 'SAVE_ZONES': 
                zone_manager.save_zones()
                log_manager.add_log("INFO", "Zonas Guardadas")
            elif act == 'LOAD_ZONES': 
                zone_manager.load_zones()
                log_manager.add_log("INFO", "Zonas Cargadas")
            elif act == 'EXIT_APP': 
                camera.release()
                cv2.destroyAllWindows()
                return
                
            elif act == 'TOGGLE_GPU': state_manager.use_gpu = not state_manager.use_gpu
            elif act == 'TOGGLE_HQ': state_manager.high_quality = not state_manager.high_quality
            
            # Slider Logic
            elif 'SLIDER' in act:
                params = act_data['params']
                mx = act_data['click_x']
                ratio = (mx - params['x_start']) / params['width']
                ratio = max(0.0, min(1.0, ratio))
                new_val = int(params['min'] + ratio * (params['max'] - params['min']))
                
                if act == 'SLIDER_SENS': 
                    thresh_val = 100 - new_val
                    state_manager.threshold = max(1, thresh_val)
                elif act == 'SLIDER_AREA': 
                    state_manager.min_area = new_val
                elif act == 'SLIDER_ZOOM': 
                    val_float = new_val / 100.0
                    app_state.zoom_level = val_float
                    state_manager.zoom_level = val_float

        # 7. Show Window
        cv2.imshow(window_name, canvas)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == 32: # SPACE BAR
             app_state.is_hand_mode = not app_state.is_hand_mode
             mode_msg = "Activado Modo MANO (Panning)" if app_state.is_hand_mode else "Activado Modo DIBUJO"
             log_manager.add_log("INFO", mode_msg)
        
        loop_counter += 1
        
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
