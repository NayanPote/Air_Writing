import glob
import json
import os
import subprocess
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
DESKTOP_SCRIPT = os.path.join(APP_DIR, "air_writing_desktop.py")

COLOR_OPTIONS = {
    "Magenta": (255, 0, 255),
    "Yellow": (0, 255, 255),
    "Green": (0, 255, 0),
    "Red": (0, 0, 255),
    "Blue": (255, 0, 0),
    "White": (255, 255, 255),
}

st.set_page_config(page_title="Air Writing", page_icon="\u270D\uFE0F", layout="wide")


def save_config(mode, color_name, brush_thickness):
    with open(CONFIG_PATH, "w") as f:
        json.dump(
            {"mode": mode, "color_name": color_name, "brush_thickness": brush_thickness},
            f,
        )


def launch_desktop_app():
    """
    Launches air_writing_desktop.py as its own process with its own
    native window. Non-blocking: Streamlit keeps running normally while
    the camera window is open.
    """
    subprocess.Popen([sys.executable, DESKTOP_SCRIPT], cwd=APP_DIR)


def main():
    st.title("\u270D\uFE0F Air Writing")
    st.caption(
        "Draw in the air with your fingertip and a webcam — powered by "
        "MediaPipe hand tracking and OpenCV."
    )

    st.info(
        "This panel configures your session and launches a native camera "
        "window (more reliable on Windows than browser-based video). "
        "Once you click Launch, a separate window will open with your "
        "live camera feed.",
        icon="\u2139\uFE0F",
    )

    with st.form("settings_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            color_name = st.selectbox("Brush color", list(COLOR_OPTIONS.keys()), index=0)
        with col2:
            brush_thickness = st.slider("Brush thickness", 2, 30, 8)
        with col3:
            mode = st.radio("Mode", ["Draw", "Erase"], horizontal=True)

        launch_clicked = st.form_submit_button(
            "\U0001F680 Launch Air Writing", use_container_width=True
        )

    if launch_clicked:
        save_config(mode.lower(), color_name, brush_thickness)
        try:
            launch_desktop_app()
            st.success(
                "Launched! Look for a new window titled "
                "'Air Writing - Desktop Mode'. It may take a few seconds "
                "to open the camera."
            )
        except Exception as e:
            st.error(f"Couldn't launch the camera window: {e}")

    st.divider()
    st.subheader("Gestures & keyboard shortcuts")
    left, right = st.columns(2)

    with left:
        st.markdown(
            "**Hand gestures**\n"
            "- Index finger up only \u2192 draws a stroke\n"
            "- Index + middle finger up \u2192 hover, no drawing\n"
            "- Fist / hand hidden \u2192 pen lifted"
        )
    with right:
        st.markdown(
            "**Keyboard shortcuts (in the camera window)**\n"
            "- `d` draw \u00b7 `e` erase \u00b7 `c` clear canvas\n"
            "- `s` save drawing \u00b7 `1`-`6` change color\n"
            "- `+` / `-` brush thickness \u00b7 `q` / `Esc` quit"
        )

    st.divider()
    st.subheader("\U0001F5BC\uFE0F Saved drawings")

    saved_files = sorted(
        glob.glob(os.path.join(APP_DIR, "air_writing*.png")), reverse=True
    )

    if not saved_files:
        st.info("No saved drawings yet. Press 's' in the camera window to save one.")
    else:
        cols = st.columns(min(4, len(saved_files)))
        for idx, file_path in enumerate(saved_files):
            with cols[idx % len(cols)]:
                st.image(file_path, caption=os.path.basename(file_path))
                with open(file_path, "rb") as f:
                    st.download_button(
                        "\u2B07\uFE0F Download",
                        data=f.read(),
                        file_name=os.path.basename(file_path),
                        mime="image/png",
                        key=f"dl_{idx}",
                    )

    with st.expander("Prefer the browser-based (WebRTC) version instead?"):
        st.markdown(
            "There's also an experimental in-browser version that streams "
            "the webcam directly into this page instead of opening a "
            "separate window. It depends on WebRTC working on your network "
            "and can fail silently (gray box) behind some VPNs, antivirus "
            "tools, or corporate firewalls.\n\n"
            "Run it with:\n```bash\nstreamlit run app_webrtc.py\n```"
        )


if __name__ == "__main__":
    main()
