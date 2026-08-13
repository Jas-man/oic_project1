
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from calculations import generate_mock_sensor_data, run_full_assessment
from weather_service import WeatherAPIError, fetch_weather_by_postcode

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY", "")

app = FastAPI(title="WESH — Live Window Efficiency Score Calculator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CalculateRequest(BaseModel):
    name: str
    postcode: str
    property_type: str = Field(pattern=r"^(house|flat|business)$")
    window_type: str = Field(pattern=r"^(single-glazed|double-glazed|triple-glazed|idk)$")
    window_height: float = Field(gt=0)
    window_width: float = Field(gt=0)
    has_sensor: bool = False


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/weather/{postcode}")
def get_weather(postcode: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="WEATHER_API_KEY not configured")
    try:
        return fetch_weather_by_postcode(postcode, API_KEY)
    except WeatherAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/calculate")
def calculate(req: CalculateRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="WEATHER_API_KEY not configured")

    try:
        weather = fetch_weather_by_postcode(req.postcode, API_KEY)
    except WeatherAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))

    sensor = generate_mock_sensor_data()
    area = req.window_height * req.window_width

    results = run_full_assessment(
        temp_outside=weather["temp_outside"],
        wind_speed_ms=weather["wind_speed"],
        humidity=weather["humidity"],
        temp_glass=sensor["temp_glass"],
        temp_amb=sensor["temp_amb"],
        air_sensor=sensor["air_sensor"],
        window_area=area,
    )

    return {
        "user": req.name,
        "postcode": req.postcode,
        "property_type": req.property_type,
        "window_type": req.window_type,
        "window_area_m2": round(area, 2),
        "weather": weather,
        "sensor_data": sensor,
        "results": results,
    }
