import cv2
import settings
import time

def test_camera():
    source = settings.WEBCAM_PATH
    print(f"Testing camera source: {source}")
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print("Error: Could not open video source.")
        print("Check if the IP is correct and the camera app is running.")
        return
    
    print("Camera opened successfully! Capturing 5 frames...")
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i+1} captured: {frame.shape}")
        else:
            print(f"Failed to capture frame {i+1}")
        time.sleep(0.5)
    
    cap.release()
    print("Test complete.")

if __name__ == "__main__":
    test_camera()
