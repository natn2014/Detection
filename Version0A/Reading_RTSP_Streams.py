import subprocess

def read_rtsp_stream(rtsp_url):
    """
    Reads and displays an RTSP stream using GStreamer.
    Args:
        rtsp_url (str): The RTSP URL to read the stream from.
    """
    gst_command = f"""
    gst-launch-1.0 rtspsrc location={rtsp_url} ! \
    rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
    """
    print(f"Reading RTSP stream from {rtsp_url}")
    subprocess.Popen(gst_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    # Read RTSP streams from the Raspberry Pi
    read_rtsp_stream(rtsp_url="rtsp://<raspberry_pi_ip>:8554")  # Camera 1
    read_rtsp_stream(rtsp_url="rtsp://<raspberry_pi_ip>:8555")  # Camera 2

    print("Reading RTSP streams. Press Ctrl+C to exit.")
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        print("RTSP streams stopped.")
