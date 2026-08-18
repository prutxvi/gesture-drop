# -*- coding: utf-8 -*-
from __future__ import annotations
"""gesture_sender module."""

import os
import time

import cv2
import mediapipe as mp
import pyperclip
import requests

SERVER_URL = os.getenv("GESTURE_DROP_SERVER", "http://127.0.0.1:5000")

# Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Used to prevent multiple triggers
last_trigger_time = 0
cooldown_seconds = 3

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("[!] Could not open webcam")

print("[OK] Showing webcam... Make a CLOSED FIST to send text")


def is_closed_fist(hand_landmarks) -> bool:
    tip_ids = [8, 12, 16, 20]
    fingers_folded = 0
    for tip_id in tip_ids:
        tip_y = hand_landmarks.landmark[tip_id].y
        lower_y = hand_landmarks.landmark[tip_id - 2].y
        if tip_y > lower_y:
            fingers_folded += 1
    return fingers_folded == 4


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if is_closed_fist(hand_landmarks):
                current_time = time.time()
                if current_time - last_trigger_time > cooldown_seconds:
                    text = pyperclip.paste()
                    if text.strip():
                        print("[OK] Copied Text:", text[:80])
                        try:
                            res = requests.post(
                                f"{SERVER_URL}/save",
                                json={"text": text},
                                timeout=5,
                            )
                            if res.status_code == 200:
                                print("[OK] Text sent to phone!")
                            else:
                                print("[!] Server returned", res.status_code)
                        except requests.RequestException:
                            print("[!] Failed to connect to server")
                    else:
                        print("[!] Clipboard is empty!")
                    last_trigger_time = current_time

    cv2.imshow("Gesture Detection", frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
