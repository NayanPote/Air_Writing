import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, frame, draw=False):
        """Runs detection on a BGR frame and optionally draws the skeleton."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        return frame

    def get_landmark_positions(self, frame):
        """Returns a list of (id, x, y) pixel coordinates for the first hand found."""
        h, w, _ = frame.shape
        landmark_list = []

        if self.results and self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            for idx, lm in enumerate(hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append((idx, cx, cy))

        return landmark_list

    def fingers_up(self, landmark_list):
        """
        Returns [thumb, index, middle, ring, pinky] as booleans indicating
        which fingers are extended. Assumes a front-facing camera view.
        """
        if not landmark_list:
            return [False] * 5

        lm = {idx: (x, y) for idx, x, y in landmark_list}
        fingers = [lm[4][0] > lm[3][0]]  # thumb via x-comparison

        for tip_id in (8, 12, 16, 20):
            fingers.append(lm[tip_id][1] < lm[tip_id - 2][1])

        return fingers

    @staticmethod
    def distance(p1, p2):
        return float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))
