import time

import av
import cv2

from backend.hand_tracker import HandTracker
from backend.canvas_utils import create_blank_canvas, overlay_canvas, put_mode_label

try:
    from streamlit_webrtc import VideoProcessorBase
except ImportError:  # allows unit-testing this module without streamlit installed
    class VideoProcessorBase:
        pass


class AirWritingProcessor(VideoProcessorBase):
    def __init__(self):
        self.tracker = HandTracker(max_hands=1)
        self.canvas = None
        self.prev_point = None

        self.brush_color = (255, 0, 255)  # BGR
        self.brush_thickness = 8
        self.eraser_thickness = 60
        self.mode = "draw"  # "draw" or "erase"

        self.clear_flag = False
        self.last_frame_time = time.time()
        self.fps = 0.0

    # --- setters called from the Streamlit UI thread ---
    def set_color(self, bgr_color):
        self.brush_color = bgr_color

    def set_brush_thickness(self, thickness):
        self.brush_thickness = int(thickness)

    def set_mode(self, mode):
        self.mode = mode

    def request_clear(self):
        self.clear_flag = True

    # --- main per-frame callback ---
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        if self.canvas is None or self.canvas.shape[:2] != (h, w):
            self.canvas = create_blank_canvas(h, w)

        if self.clear_flag:
            self.canvas = create_blank_canvas(h, w)
            self.clear_flag = False
            self.prev_point = None

        now = time.time()
        dt = now - self.last_frame_time
        self.fps = 1.0 / dt if dt > 0 else 0.0
        self.last_frame_time = now

        img = self.tracker.find_hands(img, draw=True)
        landmarks = self.tracker.get_landmark_positions(img)

        label, label_color = "No hand detected", (0, 0, 255)

        if landmarks:
            fingers = self.tracker.fingers_up(landmarks)
            index_tip = landmarks[8][1:]
            middle_up = fingers[2]
            index_up = fingers[1]

            if index_up and middle_up:
                # Hover / selection mode: move without drawing
                self.prev_point = None
                label, label_color = "Hover (select mode)", (255, 255, 0)
                cv2.circle(img, index_tip, 12, self.brush_color, cv2.FILLED)

            elif index_up and not middle_up:
                cv2.circle(img, index_tip, 8, self.brush_color, cv2.FILLED)

                if self.prev_point is None:
                    self.prev_point = index_tip

                if self.mode == "erase":
                    thickness, draw_color = self.eraser_thickness, (0, 0, 0)
                    label, label_color = "Erasing", (0, 165, 255)
                else:
                    thickness, draw_color = self.brush_thickness, self.brush_color
                    label, label_color = "Drawing", (0, 255, 0)

                cv2.line(self.canvas, self.prev_point, index_tip, draw_color, thickness)
                self.prev_point = index_tip

            else:
                self.prev_point = None
                label, label_color = "Hand idle (pen up)", (200, 200, 200)
        else:
            self.prev_point = None

        img = overlay_canvas(img, self.canvas)
        put_mode_label(img, f"{label}  |  {self.fps:4.1f} FPS", label_color)

        return av.VideoFrame.from_ndarray(img, format="bgr24")
