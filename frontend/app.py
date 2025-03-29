import streamlit as st
import requests
from PIL import Image
import io

st.title("CO2 Breakthrough Curve Analysis")

# File upload
uploaded_file = st.file_uploader("Upload your .dat file", type=["dat"])

# User input for column names
time_column = st.text_input("Enter the column name for time (sec):", "time")
co2_column = st.text_input("Enter the column name for CO2%:", "co2")

# Sliders for parameters
flow_rate = st.slider("Flow Rate (sccm)", min_value=10, max_value=500, value=100)
start_time = st.slider("Start Time (sec)", min_value=0, max_value=3600, value=0)
end_time = st.slider("End Time (sec)", min_value=0, max_value=3600, value=600)

if uploaded_file is not None:
    files = {"file": uploaded_file.getvalue()}
    data = {
        "time_column": time_column,
        "co2_column": co2_column,
        "flow_rate": flow_rate,
        "start_time": start_time,
        "end_time": end_time,
    }
    
    response = requests.post("http://127.0.0.1:8000/upload/", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        st.write("### CO2 Volume Calculated:")
        st.write(f"{result['co2_volume']} cm³")
        
        # Fetch and display plot
        plot_response = requests.get("http://127.0.0.1:8000/plot/")
        if plot_response.status_code == 200:
            image = Image.open(io.BytesIO(plot_response.content))
            st.image(image, caption="CO2 Concentration vs Time")
        else:
            st.error("Error loading the plot.")
    else:
        st.error("Error processing file. Please check your inputs.")
