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
    st.markdown("### 📷 Cloud Scanner")
    st.info("Since this app is hosted on the cloud, please use the native camera tool below to snap a picture of your waste items.")
    
    camera_image = st.camera_input("Scan Waste")
    
    if camera_image is not None:
        image = Image.open(camera_image)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        st_frame = st.empty()
        _display_detected_frames(model, st_frame, image)
