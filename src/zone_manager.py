import cv2
import numpy as np
import json
import os

class ZoneManager:
    def __init__(self):
        self.zones = [] # List of polygons (numpy arrays)
        self.current_zone = [] # Temporary list of points for the zone being drawn
        self.zone_types = [] # Could be 'forbidden', 'safe'. For now assuming all are forbidden as per prompt logic primarily.
        
    def add_point(self, x, y):
        """Adds a point to the current zone being drawn."""
        self.current_zone.append([x, y])

    def close_zone(self):
        """Finalizes the current zone if it has enough points."""
        if len(self.current_zone) > 2:
            self.zones.append(np.array(self.current_zone, dtype=np.int32))
            self.current_zone = []
            return True
        self.current_zone = []
        return False

    def clear_current_zone(self):
         self.current_zone = []

    def clear_all_zones(self):
        self.zones = []
        self.current_zone = []

    def get_zones(self):
        return self.zones

    def get_current_zone_points(self):
        return self.current_zone

    def check_intersection(self, point):
        """Checks if a point is inside any prohibited zone."""
        # point is (x, y)
        for zone in self.zones:
            # pointPolygonTest returns > 0 if inside, 0 if on edge, < 0 if outside
            if cv2.pointPolygonTest(zone, point, False) >= 0:
                return True
        return False

    def save_zones(self, filename="zones.json"):
        # Convert numpy arrays to lists for JSON serialization
        serializable_zones = [z.tolist() for z in self.zones]
        try:
            with open(filename, 'w') as f:
                json.dump(serializable_zones, f)
            print(f"[INFO] Zones saved to {filename}")
        except Exception as e:
            print(f"[ERROR] Could not save zones: {e}")

    def load_zones(self, filename="zones.json"):
        if not os.path.exists(filename):
            print("[INFO] No zone file found.")
            return
        try:
            with open(filename, 'r') as f:
                loaded_zones = json.load(f)
            self.zones = [np.array(z, dtype=np.int32) for z in loaded_zones]
            print(f"[INFO] Loaded {len(self.zones)} zones from {filename}")
        except Exception as e:
            print(f"[ERROR] Could not load zones: {e}")
