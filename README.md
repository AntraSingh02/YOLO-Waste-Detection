---
title: Intelligent Waste Segregation
emoji: ♻️
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: "1.37.0"
app_file: app.py
pinned: false
---

# ♻️ Intelligent Waste Segregation System

This project demonstrates AI-powered waste detection using a specialized **YOLOv8** (You Only Look Once) object detection model. It classifies recyclable, non-recyclable, and hazardous waste items in real-time.

## 🚀 Features
- **Real-Time Detection:** Rapid identification of waste items via your local webcam using OpenCV rendering.
- **Cloud Connectivity Solutions:** Includes a reliable native camera snapshot interface built to bypass strict cloud firewalls (perfect for Hugging Face Spaces and Streamlit Community Cloud).
- **Categorization & Logging:** Visually sorts items and maintains an automated history of your waste bins.

---

## 💻 Local Installation

To run this application efficiently on your own machine using real-time video monitoring:

**1. Clone the Repository:**
```bash
git clone https://github.com/AntraSingh02/YOLO-Waste-Detection.git
cd YOLO-Waste-Detection
```

**2. Install Dependencies:**
```bash
pip install -r used/requirements.txt
```

**3. Run the Application:**
```bash
streamlit run used/app.py
```
*Navigate to http://localhost:8501 to interact with the continuous webcam scanner.*

---

## ☁️ Cloud Deployment (Streamlit Cloud & Hugging Face)

Because cloud hosting platforms safely isolate camera drivers from python backend processes, the system provides a dual-variant setup (`app_cloud.py`) replacing continuous video buffers with a static native camera tool.

**To deploy remotely:**
- On **Streamlit Cloud**, connect your repository and configure the **Main file path** to: `used/app_cloud.py`
- On **Hugging Face Spaces**, the repository natively processes the `app.py` routing, allowing for direct deployments. 

---

## 🗂️ Project Structure

- `used/app.py`: Main Streamlit file running continuous OpenCV realtime inference.
- `used/app_cloud.py`: Cloud-optimized app using robust native single-snap photo handling.
- `used/helper.py` & `used/helper_cloud.py`: Core logic combining YOLO inferences with local rendering.
- `settings.py`: Global configuration mappings, ML models, and waste classifications.

## 🗑️ Waste Taxonomies

- **RECYCLABLE** = `['cardboard_box', 'can', 'plastic_bottle_cap', 'plastic_bottle', 'reuseable_paper']`
- **NON_RECYCLABLE** = `['plastic_bag', 'scrap_paper', 'stick', 'plastic_cup', 'snack_bag', 'plastic_box', 'straw', 'plastic_cup_lid', 'scrap_plastic', 'cardboard_bowl', 'plastic_cultery']`
- **HAZARDOUS** = `['battery', 'chemical_spray_can', 'chemical_plastic_bottle', 'chemical_plastic_gallon', 'light_bulb', 'paint_bucket']`
