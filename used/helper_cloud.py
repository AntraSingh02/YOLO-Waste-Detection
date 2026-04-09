from ultralytics import YOLO
import time
import streamlit as st
import cv2
import settings
import threading
import numpy as np
from PIL import Image

def load_model(model_path):
    model = YOLO(model_path)
    return model

def classify_waste_type(detected_items):
    recyclable_items = set(detected_items) & set(settings.RECYCLABLE)
    non_recyclable_items = set(detected_items) & set(settings.NON_RECYCLABLE)
    hazardous_items = set(detected_items) & set(settings.HAZARDOUS)
    return recyclable_items, non_recyclable_items, hazardous_items

def remove_dash_from_class_name(class_name):
    return class_name.replace("_", " ")

def _display_detected_frames(model, st_frame, image):
    image = cv2.resize(image, (640, int(640*(9/16))))
    
    if 'unique_classes' not in st.session_state:
        st.session_state['unique_classes'] = set()

    if 'recyclable_placeholder' not in st.session_state:
        st.session_state['recyclable_placeholder'] = st.sidebar.empty()
    if 'non_recyclable_placeholder' not in st.session_state:
        st.session_state['non_recyclable_placeholder'] = st.sidebar.empty()
    if 'hazardous_placeholder' not in st.session_state:
        st.session_state['hazardous_placeholder'] = st.sidebar.empty()

    if 'last_detection_time' not in st.session_state:
        st.session_state['last_detection_time'] = 0
    
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    
    if 'bins' not in st.session_state:
        st.session_state['bins'] = {
            "Recyclable": {"count": 0, "items": []},
            "Non-Recyclable": {"count": 0, "items": []},
            "Hazardous": {"count": 0, "items": []}
        }

    res = model.predict(image, conf=0.6)
    names = model.names
    detected_items = set()

    for result in res:
        new_classes = set([names[int(c)] for c in result.boxes.cls])
        if new_classes != st.session_state['unique_classes']:
            st.session_state['unique_classes'] = new_classes
            st.session_state['recyclable_placeholder'].markdown('')
            st.session_state['non_recyclable_placeholder'].markdown('')
            st.session_state['hazardous_placeholder'].markdown('')
            detected_items.update(st.session_state['unique_classes'])

            recyclable_items, non_recyclable_items, hazardous_items = classify_waste_type(detected_items)

            if recyclable_items:
                detected_items_str = "\n- ".join(remove_dash_from_class_name(item) for item in recyclable_items)
                st.session_state['recyclable_placeholder'].markdown(
                    f"<div class='stRecyclable'>Recyclable items:\n\n- {detected_items_str}</div>",
                    unsafe_allow_html=True
                )
            if non_recyclable_items:
                detected_items_str = "\n- ".join(remove_dash_from_class_name(item) for item in non_recyclable_items)
                st.session_state['non_recyclable_placeholder'].markdown(
                    f"<div class='stNonRecyclable'>Non-Recyclable items:\n\n- {detected_items_str}</div>",
                    unsafe_allow_html=True
                )
            if hazardous_items:
                detected_items_str = "\n- ".join(remove_dash_from_class_name(item) for item in hazardous_items)
                st.session_state['hazardous_placeholder'].markdown(
                    f"<div class='stHazardous'>Hazardous items:\n\n- {detected_items_str}</div>",
                    unsafe_allow_html=True
                )
            
            timestamp = time.strftime("%H:%M:%S")
            for item in recyclable_items:
                item_name = remove_dash_from_class_name(item)
                st.session_state['history'].append({"time": timestamp, "item": item_name, "category": "Recyclable"})
                st.session_state['bins']['Recyclable']['count'] += 1
                st.session_state['bins']['Recyclable']['items'].append(item_name)
                
            for item in non_recyclable_items:
                item_name = remove_dash_from_class_name(item)
                st.session_state['history'].append({"time": timestamp, "item": item_name, "category": "Non-Recyclable"})
                st.session_state['bins']['Non-Recyclable']['count'] += 1
                st.session_state['bins']['Non-Recyclable']['items'].append(item_name)
                
            for item in hazardous_items:
                item_name = remove_dash_from_class_name(item)
                st.session_state['history'].append({"time": timestamp, "item": item_name, "category": "Hazardous"})
                st.session_state['bins']['Hazardous']['count'] += 1
                st.session_state['bins']['Hazardous']['items'].append(item_name)

            st.session_state['last_detection_time'] = time.time()

    res_plotted = res[0].plot()
    st_frame.image(res_plotted, channels="BGR")

def play_webcam(model):
    from streamlit_webrtc import webrtc_streamer
    import av
    st.markdown("### 📷 Live Cloud Stream (WebRTC)")
    st.info("Ensure you are hosting this on a platform with proper STUN/TURN server access if using strict firewalls.")
    
    if 'detection_queue' not in st.session_state:
        import queue
        st.session_state.detection_queue = queue.Queue()

    def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        res = model.predict(image, conf=0.6)
        
        # Extract classes for tracking stats
        names = model.names
        detected_classes = [names[int(c)] for c in res[0].boxes.cls]
        
        if detected_classes:
            st.session_state.detection_queue.put(detected_classes)

        res_plotted = res[0].plot()
        return av.VideoFrame.from_ndarray(res_plotted, format="bgr24")

    ctx = webrtc_streamer(
        key="waste-detection",
        video_frame_callback=video_frame_callback,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False}
    )

    if st.button('🔄 Refresh Statistics from Stream'):
        import queue
        all_classes_detected = set()
        while not st.session_state.detection_queue.empty():
            try:
                frame_classes = st.session_state.detection_queue.get_nowait()
                all_classes_detected.update(frame_classes)
            except queue.Empty:
                break
        
        if all_classes_detected:
            recyclable, non_recyclable, hazardous = classify_waste_type(all_classes_detected)
            timestamp = time.strftime("%H:%M:%S")

            if 'bins' not in st.session_state:
                st.session_state['bins'] = {
                    "Recyclable": {"count": 0, "items": []},
                    "Non-Recyclable": {"count": 0, "items": []},
                    "Hazardous": {"count": 0, "items": []}
                }
            if 'history' not in st.session_state:
                st.session_state['history'] = []

            for items, cat in [(recyclable, "Recyclable"), (non_recyclable, "Non-Recyclable"), (hazardous, "Hazardous")]:
                for item in items:
                    item_name = remove_dash_from_class_name(item)
                    st.session_state['bins'][cat]['count'] += 1
                    st.session_state['bins'][cat]['items'].append(item_name)
                    st.session_state['history'].append({"time": timestamp, "item": item_name, "category": cat})
            st.success(f"Statistics refreshed! Processed {len(all_classes_detected)} items from the live stream.")
            st.rerun()
