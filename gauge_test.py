import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pytesseract
import time

# Initialize variables for plotting
values = []
timestamps = []

# Plot setup
plt.ion()
fig, ax = plt.subplots()
ax.set_title('Analog Gauge Readings')
ax.set_xlabel('Timestamp (s)')
ax.set_ylabel('Gauge Value')
line, = ax.plot([], [], label="Gauge Value")
ax.legend()

def plot_live(timestamp, value):
    timestamps.append(timestamp)
    values.append(value)
    line.set_xdata(timestamps)
    line.set_ydata(values)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

def process_frame(frame):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Threshold the image
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    extracted_number = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter out small objects
        if w > 20 and h > 20:
            # Crop the region containing the number
            roi = gray[y:y+h, x:x+w]
            
            # Perform OCR to extract the number
            text = pytesseract.image_to_string(roi, config='--psm 10 digits')
            if text.isdigit():
                extracted_number = int(text)
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Gauge: {extracted_number}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                break  # Process only the first detected number
    
    return frame, extracted_number

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Webcam not accessible.")
    exit()

start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break
    
    processed_frame, value = process_frame(frame)
    
    # If a number is detected, plot and display it
    if value is not None:
        elapsed_time = round(time.time() - start_time, 2)
        plot_live(elapsed_time, value)
    
    cv2.imshow("Analog Gauge Detection", processed_frame)
    
    # Break loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()
