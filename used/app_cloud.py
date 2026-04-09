import streamlit as st
import helper_cloud as helper
import settings
from pathlib import Path

st.set_page_config(
    page_title="Waste Detection (Cloud Version)",
)

st.sidebar.title("Detect Console")

model_path = Path(settings.DETECTION_MODEL)

st.title("Intelligent waste segregation system (Cloud)")
st.write("Since this is deployed online, please use the scanner to take a photo of the waste.")
st.markdown(
"""
<style>
    .stRecyclable { background-color: rgba(233,192,78,255); padding: 1rem 0.75rem; margin-bottom: 1rem; border-radius: 0.5rem; font-size:18px !important; }
    .stNonRecyclable { background-color: rgba(94,128,173,255); padding: 1rem 0.75rem; margin-bottom: 1rem; border-radius: 0.5rem; font-size:18px !important; }
    .stHazardous { background-color: rgba(194,84,85,255); padding: 1rem 0.75rem; margin-bottom: 1rem; border-radius: 0.5rem; font-size:18px !important; }
    .stLog { background-color: rgba(240, 242, 246, 0.8); padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #ddd; }
    .containerIndicator { text-align: center; padding: 10px; border-radius: 10px; color: white; font-weight: bold; margin-bottom: 20px; }
    .binCard { background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 8px solid #ddd; }
    .binTitle { font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .binCount { font-size: 2.5rem; font-weight: bold; }
</style>
""",
unsafe_allow_html=True
)

try:
    model = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)

helper.play_webcam(model)

st.divider()
st.subheader("🗑️ Waste Bin Inventory")

if 'bins' in st.session_state:
    cols = st.columns(3)
    bin_types = [
        {"name": "Recyclable", "color": "#e9c04e", "icon": "♻️"},
        {"name": "Non-Recyclable", "color": "#5e80ad", "icon": "🚫"},
        {"name": "Hazardous", "color": "#c25455", "icon": "⚠️"}
    ]
    
    for i, b in enumerate(bin_types):
        with cols[i]:
            count = st.session_state['bins'][b['name']]['count']
            st.markdown(f"""
                <div class='binCard' style='border-top-color: {b['color']}'>
                    <div class='binTitle'>{b['icon']} {b['name']}</div>
                    <div class='binCount'>{count}</div>
                    <small>Items Stored</small>
                </div>
            """, unsafe_allow_html=True)
            
            items = st.session_state['bins'][b['name']]['items']
            if items:
                with st.expander("View Contents"):
                    st.write(", ".join(items[-20:]))

    st.write("")
    if st.button("Clear All Bins"):
        st.session_state['bins'] = {
            "Recyclable": {"count": 0, "items": []},
            "Non-Recyclable": {"count": 0, "items": []},
            "Hazardous": {"count": 0, "items": []}
        }
        st.session_state['history'] = []
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("Recent Detections")
if 'history' in st.session_state and st.session_state['history']:
    for entry in reversed(st.session_state['history'][-10:]):
        color = "#e9c04e" if entry['category'] == "Recyclable" else "#5e80ad" if entry['category'] == "Non-Recyclable" else "#c25455"
        st.sidebar.markdown(f"""
        <div class='stLog' style='border-left: 5px solid {color}'>
            <b>{entry['time']}</b><br/>
            Item: {entry['item']}<br/>
            Target: <i>{entry['category']} Bin</i>
        </div>
        """, unsafe_allow_html=True)
