import cv2
import numpy as np


def create_blank_canvas(height, width):
    return np.zeros((height, width, 3), dtype=np.uint8)


def overlay_canvas(frame, canvas):
    """
    Merges the ink canvas onto the live frame: pixels that have been
    drawn on replace the camera image, everything else shows the feed.
    """
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)

    return cv2.add(frame_bg, canvas_fg)


def put_mode_label(frame, text, color):
    cv2.rectangle(frame, (0, 0), (260, 40), (30, 30, 30), -1)
    cv2.putText(
        frame, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA
    )
