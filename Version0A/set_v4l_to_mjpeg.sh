#!/bin/bash

# Script to configure all V4L2 devices to MJPEG format and optional resolution/frame rate
# Requires v4l-utils (v4l2-ctl)

# Desired resolution and frame rate (modify as needed)
RES_WIDTH=640
RES_HEIGHT=480
FPS=30
FORMAT="MJPG"

# List all video devices
VIDEO_DEVICES=$(ls /dev/video* 2>/dev/null)

if [ -z "$VIDEO_DEVICES" ]; then
    echo "No video devices found!"
    exit 1
fi

echo "Setting all V4L2 devices to format: $FORMAT, resolution: ${RES_WIDTH}x${RES_HEIGHT}, frame rate: $FPS FPS"

for DEVICE in $VIDEO_DEVICES; do
    echo "Configuring $DEVICE..."
    
    # Check if MJPEG is supported by this device
    FORMATS=$(v4l2-ctl --device=$DEVICE --list-formats | grep "$FORMAT")
    if [ -z "$FORMATS" ]; then
        echo "  $DEVICE does not support MJPEG format! Skipping..."
        continue
    fi

    # Set format to MJPEG
    v4l2-ctl --device=$DEVICE --set-fmt-video=width=$RES_WIDTH,height=$RES_HEIGHT,pixelformat=$FORMAT
    if [ $? -eq 0 ]; then
        echo "  Format set to $FORMAT with resolution ${RES_WIDTH}x${RES_HEIGHT}"
    else
        echo "  Failed to set format on $DEVICE"
        continue
    fi

    # Set frame rate
    v4l2-ctl --device=$DEVICE --set-parm=$FPS
    if [ $? -eq 0 ]; then
        echo "  Frame rate set to $FPS FPS"
    else
        echo "  Failed to set frame rate on $DEVICE"
    fi

    echo "  $DEVICE configured successfully!"
done

echo "All devices configured!"
