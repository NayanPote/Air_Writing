import cv2
import streamlit as st
from streamlit_webrtc import RTCConfiguration, WebRtcMode, webrtc_streamer

from backend.air_writing_processor import AirWritingProcessor

st.set_page_config(page_title="Air Writing", page_icon="\u270D\uFE0F", layout="wide")

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

COLOR_OPTIONS = {
    "Magenta": (255, 0, 255),
    "Yellow": (0, 255, 255),
    "Green": (0, 255, 0),
    "Red": (0, 0, 255),
    "Blue": (255, 0, 0),
    "White": (255, 255, 255),
}


def main():
    st.title("\u270D\uFE0F Air Writing")
    st.caption(
        "Draw in the air using just your fingertip and a webcam — "
        "powered by MediaPipe hand tracking and OpenCV."
    )

    with st.sidebar:
        st.header("Controls")

        color_name = st.selectbox("Brush color", list(COLOR_OPTIONS.keys()), index=0)
        brush_size = st.slider("Brush thickness", min_value=2, max_value=30, value=8)
        mode = st.radio("Mode", ["Draw", "Erase"], horizontal=True)
        clear_clicked = st.button("\U0001F9F9 Clear Canvas", use_container_width=True)

        st.divider()
        st.subheader("Gestures")
        st.markdown(
            "- **Index finger up only** \u2192 draws a stroke\n"
            "- **Index + middle finger up** \u2192 hover, no drawing\n"
            "- **Fist / hand hidden** \u2192 pen lifted\n"
            "- Switch to **Erase** to remove ink with the same gestures"
        )

        st.divider()
        st.caption(
            "If the camera doesn't start, check that your browser has been "
            "given camera permission for this site."
        )

    ctx = webrtc_streamer(
        key="air-writing",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=AirWritingProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if ctx.video_processor:
        ctx.video_processor.set_color(COLOR_OPTIONS[color_name])
        ctx.video_processor.set_brush_thickness(brush_size)
        ctx.video_processor.set_mode("erase" if mode == "Erase" else "draw")
        if clear_clicked:
            ctx.video_processor.request_clear()

    st.divider()
    st.subheader("\U0001F4BE Save your drawing")

    if ctx.video_processor and ctx.video_processor.canvas is not None:
        if st.button("Capture current canvas"):
            canvas_bgr = ctx.video_processor.canvas
            canvas_rgb = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)
            st.image(canvas_rgb, caption="Your air-written canvas", channels="RGB")

            success, buffer = cv2.imencode(".png", canvas_bgr)
            if success:
                st.download_button(
                    label="\u2B07\uFE0F Download PNG",
                    data=buffer.tobytes(),
                    file_name="air_writing.png",
                    mime="image/png",
                )
    else:
        st.info("Start the camera above and draw something first.")


if __name__ == "__main__":
    main()
