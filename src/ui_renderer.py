import cv2
import numpy as np

class UIRenderer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        # Colors (BGR)
        self.C_BG = (30, 30, 30)       # Dark Grey Background
        self.C_PANEL = (50, 50, 50)    # Light Grey Panel
        self.C_ACCENT = (200, 100, 0)  # Industrial Blue/Orange accent
        self.C_TEXT = (220, 220, 220)
        self.C_GREEN = (0, 200, 0)
        self.C_RED = (0, 0, 200)
        self.C_YELLOW = (0, 255, 255)
        
        # Layout Config
        self.VIDEO_RECT = (20, 50, 860, 484) # x, y, w, h
        self.UI_START_X = 900
        
        self.hitboxes = []

    def draw_dashboard_frame(self, frame_w=1280, frame_h=720):
        """Creates the base canvas."""
        canvas = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
        canvas[:] = self.C_BG
        
        # Draw Header
        cv2.rectangle(canvas, (0, 0), (frame_w, 40), (20, 20, 20), -1)
        cv2.putText(canvas, "SISTEMA DE SEGURIDAD INDUSTRIAL - HMI PRINCIPAL", (20, 28), self.font, 0.7, self.C_TEXT, 2)
        
        # Draw Video Frame Border
        vx, vy, vw, vh = self.VIDEO_RECT
        cv2.rectangle(canvas, (vx-2, vy-2), (vx+vw+2, vy+vh+2), (100, 100, 100), 2)
        cv2.putText(canvas, "VIDEO EN VIVO (CAMARA 1)", (vx, vy-10), self.font, 0.5, self.C_TEXT, 1)

        return canvas

    def render(self, canvas, video_frame, state_manager, log_manager, metrics_data):
        self.hitboxes = [] # Reset hitboxes
        
        # 1. Draw Dashboard Background
        canvas[:] = self.C_BG
        self.draw_dashboard_frame(canvas)

        # 2. Draw Video (Aspect Ratio Safe)
        vx, vy, vw, vh = self.VIDEO_RECT
        if video_frame is not None:
            # Aspect Ratio Logic
            h_img, w_img = video_frame.shape[:2]
            aspect_ratio_img = w_img / h_img
            aspect_ratio_slot = vw / vh
            
            if aspect_ratio_img > aspect_ratio_slot:
                # Image is wider than slot (limit by width)
                final_w = vw
                final_h = int(vw / aspect_ratio_img)
                offset_y = (vh - final_h) // 2
                offset_x = 0
            else:
                # Image is taller than slot (limit by height)
                final_h = vh
                final_w = int(vh * aspect_ratio_img)
                offset_x = (vw - final_w) // 2
                offset_y = 0
            
            # Store the actual video area for mouse mapping
            self.current_video_area = (vx + offset_x, vy + offset_y, final_w, final_h)

            interp = cv2.INTER_LANCZOS4 if state_manager.high_quality else cv2.INTER_LINEAR
            try:
                resized = cv2.resize(video_frame, (final_w, final_h), interpolation=interp)
                canvas[vy+offset_y:vy+offset_y+final_h, vx+offset_x:vx+offset_x+final_w] = resized
            except Exception as e:
                print(f"Resize Error: {e}")

        # 3. Draw Controls
        self._draw_controls(canvas, state_manager)
        
        # 4. Logs & Metrics
        self._draw_logs_metrics(canvas, log_manager, metrics_data)
        
        # 5. Status
        self._draw_status_bar(canvas, state_manager)
        
        return self.hitboxes

    def draw_dashboard_frame(self, canvas):
        frame_h, frame_w = canvas.shape[:2]
        
        # Header
        cv2.rectangle(canvas, (0, 0), (frame_w, 40), (20, 20, 20), -1)
        cv2.putText(canvas, "SISTEMA DE SEGURIDAD INDUSTRIAL - HMI PRINCIPAL", (20, 28), self.font, 0.7, self.C_TEXT, 2)
        
        # Video Border
        vx, vy, vw, vh = self.VIDEO_RECT
        cv2.rectangle(canvas, (vx-2, vy-2), (vx+vw+2, vy+vh+2), (60, 60, 60), 2)
        cv2.putText(canvas, "VIDEO EN VIVO", (vx, vy-10), self.font, 0.5, self.C_TEXT, 1)

    def _draw_controls(self, canvas, state_manager):
        x_start = self.UI_START_X
        y_start = 60
        w_panel = 360
        
        # Panel Background
        cv2.rectangle(canvas, (x_start, y_start), (x_start + w_panel, y_start + 450), self.C_PANEL, -1)
        cv2.putText(canvas, "CONTROLES DE OPERACION", (x_start + 10, y_start + 25), self.font, 0.6, self.C_YELLOW, 2)
        
        # Buttons Row 1 (Modes)
        btn_y = y_start + 45
        btn_h = 60
        btn_w = 165
        
        # COLD (Grey/Blue)
        cold_color = (100, 100, 100) if state_manager.is_hot() else (200, 150, 0)
        self._draw_button(canvas, "COLD (Frio)", x_start + 10, btn_y, btn_w, btn_h, cold_color, "SET_COLD")
        
        # HOT (Red)
        hot_color = (0, 0, 180) if state_manager.is_hot() else (80, 0, 0)
        border_color = (0, 255, 255) if state_manager.is_hot() else (100, 0, 0)
        if state_manager.is_hot():
             cv2.rectangle(canvas, (x_start + 10 + btn_w + 10 - 2, btn_y-2), (x_start + 10 + btn_w + 10 + btn_w + 2, btn_y+btn_h+2), border_color, 2)
        self._draw_button(canvas, "HOT (Vigilar)", x_start + 10 + btn_w + 10, btn_y, btn_w, btn_h, hot_color, "SET_HOT")
        
        # Sliders
        slider_y = btn_y + btn_h + 40
        gap = 60
        
        # Sensitivity
        # Inverted Display Logic for UX: Show 100% when threshold is 0, 0% when threshold is 255 (or similar range)
        # Real Threshold: 0 (Sensitive) to 100 (Insensitive). 
        # Display: 100 - Real
        disp_sens = 100 - state_manager.threshold
        self._draw_slider(canvas, "SENSIBILIDAD (%)", disp_sens, 0, 100, x_start+15, slider_y, w_panel-30, "SLIDER_SENS")
        
        # Area
        slider_y += gap
        self._draw_slider(canvas, "AREA MINIMA (px)", state_manager.min_area, 100, 5000, x_start+15, slider_y, w_panel-30, "SLIDER_AREA")
        
        # Zoom
        slider_y += gap
        # Display as integer percentage (100% - 300%)
        disp_zoom = int(state_manager.zoom_level * 100)
        self._draw_slider(canvas, "ZOOM DIGITAL (%)", disp_zoom, 100, 300, x_start+15, slider_y, w_panel-30, "SLIDER_ZOOM")

        # Toggles Row
        tog_y = slider_y + 50
        
        # GPU
        proc_color = (0, 100, 0) if state_manager.use_gpu else (50, 50, 50)
        self._draw_button(canvas, "GPU ON" if state_manager.use_gpu else "GPU OFF", x_start + 10, tog_y, 105, 30, proc_color, "TOGGLE_GPU")

        # HQ
        hq_color = (0, 100, 0) if state_manager.high_quality else (50, 50, 50)
        self._draw_button(canvas, "HQ ON" if state_manager.high_quality else "HQ OFF", x_start + 125, tog_y, 105, 30, hq_color, "TOGGLE_HQ")
        
        # Save/Load/Exit Row
        sys_y = tog_y + 50
        self._draw_button(canvas, "GUARDAR", x_start + 10, sys_y, 105, 40, (0, 80, 0), "SAVE_ZONES")
        self._draw_button(canvas, "CARGAR", x_start + 125, sys_y, 105, 40, (80, 80, 0), "LOAD_ZONES")
        self._draw_button(canvas, "SALIR", x_start + 240, sys_y, 105, 40, (0, 0, 100), "EXIT_APP")


    def _draw_slider(self, canvas, label, val, min_v, max_v, x, y, w, action_tag):
        # Label
        cv2.putText(canvas, f"{label}: {val}", (x, y - 8), self.font, 0.5, self.C_TEXT, 1)
        
        # Bar Background
        cv2.rectangle(canvas, (x, y), (x + w, y + 12), (30, 30, 30), -1)
        
        # Fill
        # Clamp value just in case
        safe_val = max(min_v, min(max_v, val))
        ratio = (safe_val - min_v) / (max_v - min_v) if max_v != min_v else 0
        fill_w = int(w * ratio)
        cv2.rectangle(canvas, (x, y), (x + fill_w, y + 12), self.C_ACCENT, -1)
        
        # Handle
        cx = x + fill_w
        cy = y + 6
        cv2.circle(canvas, (cx, cy), 8, (220, 220, 220), -1)
        
        # Hitbox (Full Width for easy clicking)
        self.hitboxes.append({
            'action': action_tag,
            'rect': (x, y-10, x+w, y+20),
            'params': {'min': min_v, 'max': max_v, 'x_start': x, 'width': w}
        })

    def _draw_button(self, canvas, text, x, y, w, h, color, action):
        cv2.rectangle(canvas, (x, y), (x+w, y+h), color, -1)
        cv2.rectangle(canvas, (x, y), (x+w, y+h), (180, 180, 180), 1)
        
        text_size = cv2.getTextSize(text, self.font, 0.5, 1)[0]
        tx = x + (w - text_size[0]) // 2
        ty = y + (h + text_size[1]) // 2
        cv2.putText(canvas, text, (tx, ty), self.font, 0.5, (255, 255, 255), 1)
        
        self.hitboxes.append({'action': action, 'rect': (x, y, x+w, y+h)})

    def _draw_logs_metrics(self, canvas, log_manager, metrics):
        x = self.UI_START_X
        y = 530
        w_panel = 360
        h_panel = 180
        
        cv2.rectangle(canvas, (x, y), (x+w_panel, y+h_panel), (40, 40, 40), -1)
        self.draw_text_pil(canvas, "LOGS DEL SISTEMA", (x+10, y+20), 12, (150, 150, 255))
        
        log_y_start = y + 45
        logs = log_manager.get_logs()
        for i, log in enumerate(logs):
            if i > 5: break
            color = self.C_TEXT
            if log['type'] == 'ALARMA': color = self.C_RED
            elif log['type'] == 'INFO': color = self.C_GREEN
            
            line = f"{log['time']} {log['msg']}"
            # Use PIL for utf-8 support
            self.draw_text_pil(canvas, line, (x+10, log_y_start + i*20), 11, color)

        # Metrics at bottom of log panel
        met_y = y + h_panel - 15
        fps = metrics.get('fps', 0)
        lat = metrics.get('latency', 0)
        proc = metrics.get('proc', 'CPU')
        # Metrics are usually ASCII, keep cv2 for speed or simple consistency? 
        # Let's use PIL for consistency in this panel.
        self.draw_text_pil(canvas, f"FPS: {fps:.0f} | LAT: {lat:.1f}ms | {proc}", (x+10, met_y), 12, self.C_YELLOW)

    def draw_text_pil(self, img, text, pos, size, color):
        """
        Draws text using PIL to support UTF-8 (Accents).
        img: Numpy array (BGR)
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # Convert to PIL (RGB)
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        # Load Font (Try Arial, fallback to default)
        try:
             # Windows Path
             font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
        except:
             try:
                 font = ImageFont.truetype("arial.ttf", size)
             except:
                 font = ImageFont.load_default()
        
        # PIL uses RGB
        # color is BGR, convert to RGB
        rgb_color = (color[2], color[1], color[0])
        
        # Draw
        # pos is (x, y) - cv2 uses bottom-left, PIL uses top-left usually? 
        # Check: cv2 putText (x,y) is bottom-left of text string.
        # PIL text (x,y) is top-left.
        # We need to adjust y.
        # Approximate baseline adjustment: y - size
        draw.text((pos[0], pos[1] - size), text, font=font, fill=rgb_color)
        
        # Convert back to Numpy (BGR)
        # Note: This copy overhead is acceptable for UI
        np_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Copy back to reference. 
        # Better: we can't replace 'img' reference in-place easily like this if we re-alloc.
        # We must copy content back into 'img'.
        np.copyto(img, np_img)

    def _draw_status_bar(self, canvas, state_manager):
        # Bottom Left under video
        x = 20
        y = 600
        
        state_str = "ACTIVO (VIGILANCIA)" if state_manager.is_hot() else "ESPERA (CONFIG)"
        color = (0, 0, 255) if state_manager.is_hot() else (0, 180, 0)
        
        cv2.putText(canvas, f"ESTADO: {state_str}", (x, y), self.font, 0.8, color, 2)
        
        if state_manager.is_hot():
             cv2.putText(canvas, f"INTRUSIONES: {state_manager.intrusions}", (x, y+40), self.font, 0.8, (200, 200, 200), 2)

    def trigger_visual_alarm(self, canvas):
        # Flashing Border on Video
        if hasattr(self, 'current_video_area'):
            vx, vy, vw, vh = self.current_video_area
            cv2.rectangle(canvas, (vx-5, vy-5), (vx+vw+5, vy+vh+5), (0, 0, 255), 5)
            cv2.putText(canvas, "ALERTA DE INTRUSO", (vx + 20, vy + 50), self.font, 1.5, (0, 0, 255), 3)

    def draw_zones_on_video(self, video_frame, zone_manager, app_state):
        # This draws ON THE VIDEO FRAME BEFORE RESIZING
        # This is correct because points are in Camera Space -> Crop Space
        for zone in zone_manager.get_zones():
            pts = []
            for pt in zone:
                # Adjust for crop offset (image space -> crop space)
                cx = pt[0] - app_state.offset_x
                cy = pt[1] - app_state.offset_y
                pts.append([cx, cy])
            
            pts_arr = np.array(pts, dtype=np.int32)
            cv2.polylines(video_frame, [pts_arr], True, (0, 0, 255), 2)
            
            # Use semi-transparent overlay
            overlay = video_frame.copy()
            cv2.fillPoly(overlay, [pts_arr], (0, 0, 100))
            cv2.addWeighted(overlay, 0.4, video_frame, 0.6, 0, video_frame)
            
        # Draw active drawing
        curr = zone_manager.get_current_zone_points()
        if len(curr) > 0:
            pts = []
            for pt in curr:
                cx = pt[0] - app_state.offset_x
                cy = pt[1] - app_state.offset_y
                pts.append([cx, cy])
            pts_arr = np.array(pts, dtype=np.int32)
            
            if len(pts) > 1:
                cv2.polylines(video_frame, [pts_arr], False, (0, 255, 255), 2)
            for pt in pts:
                cv2.circle(video_frame, (pt[0], pt[1]), 3, (0, 255, 255), -1)

    def draw_detections(self, frame, contours):
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


