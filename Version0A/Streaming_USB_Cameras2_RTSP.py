import os
import subprocess

def stream_usb_camera(camera_index, rtsp_port):
    """
    Streams a USB camera to an RTSP server using GStreamer.
    Args:
        camera_index (int): The index of the USB camera (e.g., /dev/video0 -> 0).
        rtsp_port (int): The port to stream the RTSP feed to.
    """
    gst_command = f"""
    gst-launch-1.0 v4l2src device=/dev/video{camera_index} ! \
    video/x-raw,width=640,height=480,framerate=30/1 ! \
    videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! \
    rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port={rtsp_port}
    """
    print(f"Starting RTSP stream for /dev/video{camera_index} on port {rtsp_port}")
    subprocess.Popen(gst_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    # Stream two cameras to different RTSP ports
    stream_usb_camera(camera_index=0, rtsp_port=8554)  # Camera 1 -> RTSP port 8554
    stream_usb_camera(camera_index=1, rtsp_port=8555)  # Camera 2 -> RTSP port 8555

    print("Streaming started. Press Ctrl+C to exit.")
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        print("Streaming stopped.")
 Streaming USB Cameras to RTSP
