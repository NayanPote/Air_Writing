# Air Writing

Draw in the air with your fingertip using just a webcam. Built with
**MediaPipe** (hand tracking), **OpenCV** (drawing/compositing), and
**Streamlit** (control panel / UI).

There are two ways to run it. Use **desktop mode** unless you already
know browser WebRTC works reliably on your network — it's simpler and
doesn't depend on browser video streaming at all.

## Project structure

```
air_writing_app/
├── app.py                        # RECOMMENDED: Streamlit control panel + launcher
├── air_writing_desktop.py        # Native OpenCV camera window (the drawing engine)
├── app_webrtc.py                 # Optional: in-browser video via streamlit-webrtc
├── config.json                   # Settings shared between app.py and the desktop engine
├── requirements.txt
├── backend/
│   ├── __init__.py
│   ├── hand_tracker.py           # MediaPipe Hands wrapper
│   ├── canvas_utils.py           # canvas creation / overlay helpers
│   └── air_writing_processor.py  # per-frame gesture logic (used by app_webrtc.py)
└── README.md
```

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Recommended: desktop mode

```bash
streamlit run app.py
```

This opens a browser control panel where you pick brush color,
thickness, and mode, then click **Launch Air Writing**. That spawns a
native OpenCV window with your live camera feed — no browser video
streaming involved, so it isn't affected by WebRTC/network issues.
Saved drawings (press `s` in the camera window) show up back in the
Streamlit panel as a gallery you can preview and download from.

You can also skip the panel and run the camera window directly:
```bash
python air_writing_desktop.py
```

### Keyboard shortcuts (in the camera window)
- `d` draw · `e` erase · `c` clear canvas
- `s` save drawing · `1`-`6` change color
- `+` / `-` brush thickness · `q` / `Esc` quit

## Optional: browser-based (WebRTC) mode

```bash
streamlit run app_webrtc.py
```

Streams the webcam directly into the browser page using
`streamlit-webrtc`, with sliders for live in-page control. Nicer when it
works, but WebRTC needs a clean ICE/UDP path between your browser and
the app — some VPNs, antivirus network protection, or corporate
firewalls silently block it (you'll see a gray box with no video). If
that happens, use desktop mode instead.

## How the gesture logic works (both modes share this)

1. `HandTracker` (MediaPipe) finds hand landmarks each frame and reports
   which fingers are extended.
2. Gesture rules:
   - **Index finger up only** → draws a line from the previous fingertip
     position to the current one.
   - **Index + middle finger up** → "hover" mode, so you can reposition
     your hand without leaving a stroke (same convention used in classic
     virtual-painter demos).
   - **No fingers up / no hand detected** → pen lifted, stroke breaks.
3. Strokes accumulate on a persistent `canvas` (a blank image the same
   size as the video). Each frame, the canvas is composited on top of
   the live video with `overlay_canvas`, so ink stays visible while the
   rest of the frame still shows the camera feed.
4. Switching to erase mode uses the same gestures but draws in black
   with a much thicker stroke, effectively rubbing out ink.

## Notes & troubleshooting

- **Performance**: MediaPipe Hands runs on CPU by default and is fast
  enough for real-time use on most laptops. If FPS (shown in the
  overlay) is low, close other apps using the camera/GPU.
- **Right vs. left hand**: the thumb "up" check uses an x-coordinate
  comparison tuned for a right hand facing the camera; it doesn't affect
  the main drawing gesture (index finger), only optional extensions.
- **Camera already in use**: close Zoom/Teams/other apps or browser tabs
  holding the webcam before launching.
- **Desktop mode window doesn't appear**: give it a few seconds — camera
  initialization on some Windows machines takes a moment. Check the
  terminal running `streamlit run app.py` for any error output.
- **WebRTC mode shows a gray box**: this means the ICE/UDP handshake
  between your browser and the app failed — commonly caused by a VPN,
  antivirus "network protection," or a restrictive firewall/network
  policy. Use desktop mode instead of debugging this further.

## Possible extensions

- Add a "recognize handwriting" mode that feeds the saved canvas through
  an OCR model (e.g. Tesseract) to convert air-written text to a string.
- Add multi-color strokes per gesture (e.g. pinch-and-hold to open a
  color wheel).
- Support two-hand mode for symmetric drawing or a separate eraser hand.
