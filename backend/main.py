from fastapi import FastAPI, File, UploadFile, Form
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the CO2 Breakthrough API! API is working."}

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    time_column: str = Form(...),
    co2_column: str = Form(...),
    flow_rate: float = Form(...),
    start_time: float = Form(...),
    end_time: float = Form(...),
):
    # Read the .dat file
    df = pd.read_csv(io.BytesIO(file.file.read()), delimiter="\t", header=None)

    # Assign headers manually
    df.columns = ["time", "co2"]

    # Extract data
    x = df[time_column].values
    y = df[co2_column].values

    # Filter data within start and end time
    mask = (x >= start_time) & (x <= end_time)
    x_filtered = x[mask]
    y_filtered = y[mask]

    # Define baseline CO2 concentration (adjustable)
    y_line = np.min(y_filtered)

    # Compute volume of CO2 adsorbed/desorbed
    y_diff = np.abs(y_filtered - y_line)
    area_percentage_co2_sec = np.trapz(y_diff, x_filtered)
    area_fractional_co2_sec = area_percentage_co2_sec / 100
    volume_cm3 = area_fractional_co2_sec * (flow_rate / 60)

    return JSONResponse(content={"co2_volume": round(volume_cm3, 2)})

@app.get("/plot/")
async def plot_curve():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_filtered, y_filtered, label="CO2 Concentration")
    ax.axhline(y=y_line, color='r', linestyle='--', label=f'y = {y_line}')
    ax.fill_between(x_filtered, y_filtered, y_line, where=(y_filtered > y_line), interpolate=True, alpha=0.3)
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('% CO2')
    ax.legend()
    ax.set_title('CO2 Concentration vs Time')

    # Convert to image response
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")
