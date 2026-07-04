# cd air_writing_app
# python air_writing_desktop.py
import json
import os
import time

import cv2

from backend.hand_tracker import HandTracker
from backend.canvas_utils import create_blank_canvas, overlay_canvas, put_mode_label

COLOR_OPTIONS = [
    ("Magenta", (255, 0, 255)),
    ("Yellow", (0, 255, 255)),
    ("Green", (0, 255, 0)),
    ("Red", (0, 0, 255)),
    ("Blue", (255, 0, 0)),
    ("White", (255, 255, 255)),
]

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_initial_config():
    """
    Reads optional startup settings written by the Streamlit control panel
    (app.py). Falls back to sensible defaults if the file is missing or
    malformed, so this script also runs fine completely standalone.
    """
    defaults = {"mode": "draw", "color_name": "Magenta", "brush_thickness": 8}

    if not os.path.exists(CONFIG_PATH):
        return defaults

    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        defaults.update({k: data[k] for k in defaults if k in data})
    except (json.JSONDecodeError, OSError):
        pass

    return defaults


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW avoids slow-open bug on Windows
    if not cap.isOpened():
        print("ERROR: could not open webcam. Is it being used by another app?")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    tracker = HandTracker(max_hands=1)
    canvas = None
    prev_point = None

    config = load_initial_config()
    mode = config["mode"] if config["mode"] in ("draw", "erase") else "draw"
    color_names = [name for name, _ in COLOR_OPTIONS]
    color_idx = color_names.index(config["color_name"]) if config["color_name"] in color_names else 0
    brush_thickness = int(config["brush_thickness"])
    eraser_thickness = 60

    last_time = time.time()

    print("Air Writing (desktop mode) started.")
    print("Keys: d=draw  e=erase  c=clear  s=save  1-6=color  +/-=thickness  q=quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read from webcam.")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if canvas is None:
            canvas = create_blank_canvas(h, w)

        now = time.time()
        fps = 1.0 / (now - last_time) if now > last_time else 0.0
        last_time = now

        frame = tracker.find_hands(frame, draw=True)
        landmarks = tracker.get_landmark_positions(frame)

        color_name, brush_color = COLOR_OPTIONS[color_idx]
        label, label_color = "No hand detected", (0, 0, 255)

        if landmarks:
            fingers = tracker.fingers_up(landmarks)
            index_tip = landmarks[8][1:]
            index_up, middle_up = fingers[1], fingers[2]

            if index_up and middle_up:
                prev_point = None
                label, label_color = "Hover (select mode)", (255, 255, 0)
                cv2.circle(frame, index_tip, 12, brush_color, cv2.FILLED)

            elif index_up and not middle_up:
                cv2.circle(frame, index_tip, 8, brush_color, cv2.FILLED)
                if prev_point is None:
                    prev_point = index_tip

                if mode == "erase":
                    thickness, draw_color = eraser_thickness, (0, 0, 0)
                    label, label_color = "Erasing", (0, 165, 255)
                else:
                    thickness, draw_color = brush_thickness, brush_color
                    label, label_color = f"Drawing ({color_name})", (0, 255, 0)

                cv2.line(canvas, prev_point, index_tip, draw_color, thickness)
                prev_point = index_tip
            else:
                prev_point = None
                label, label_color = "Hand idle (pen up)", (200, 200, 200)
        else:
            prev_point = None

        display = overlay_canvas(frame, canvas)
        put_mode_label(display, f"{label} | {fps:4.1f} FPS | mode={mode}", label_color)

        cv2.imshow("Air Writing - Desktop Mode", display)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):  # q or Esc
            break
        elif key == ord("d"):
            mode = "draw"
        elif key == ord("e"):
            mode = "erase"
        elif key == ord("c"):
            canvas = create_blank_canvas(h, w)
            prev_point = None
        elif key == ord("s"):
            cv2.imwrite("air_writing.png", canvas)
            print("Saved canvas to air_writing.png")
        elif ord("1") <= key <= ord("6"):
            color_idx = key - ord("1")
        elif key in (ord("+"), ord("=")):
            brush_thickness = min(30, brush_thickness + 2)
        elif key in (ord("-"), ord("_")):
            brush_thickness = max(2, brush_thickness - 2)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
