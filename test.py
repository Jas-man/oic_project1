import math
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from calculations import (
    calculate_surface_temp_index,
    estimate_u_value,
    calculate_thermal_score,
    calculate_dew_point,
    calculate_humidity_score,
    calculate_air_tightness_score,
    calculate_wind_heat_loss_factor,
    calculate_overall_efficiency,
    estimate_energy_waste_kwh,
    generate_mock_sensor_data,
    run_full_assessment,
)
from weather_service import fetch_weather_by_postcode, WeatherAPIError
from main import app

client = TestClient(app)


# --- Surface temperature index ---

def test_surface_temp_index_normal():
    # glass=15, amb=21, outside=8 → (15-8)/(21-8) ≈ 0.538
    assert calculate_surface_temp_index(15, 21, 8) == pytest.approx(0.538, abs=0.001)

def test_surface_temp_index_glass_equals_outdoor():
    assert calculate_surface_temp_index(5, 20, 5) == 0.0

def test_surface_temp_index_glass_equals_ambient():
    assert calculate_surface_temp_index(20, 20, 5) == 1.0

def test_surface_temp_index_zero_delta():
    assert calculate_surface_temp_index(10, 10, 10) == 0.0


# --- U-value ---

def test_u_value_perfect_window():
    assert estimate_u_value(1.0) == 0.0

def test_u_value_worst_window():
    assert estimate_u_value(0.0) == 7.7


# --- Thermal score ---

def test_thermal_score_good():
    score = calculate_thermal_score(0.8)
    assert score == 100.0

def test_thermal_score_bad():
    score = calculate_thermal_score(5.8)
    assert score == 0.0

def test_thermal_score_mid():
    score = calculate_thermal_score(3.3)
    assert 0.0 < score < 100.0


# --- Dew point ---

def test_dew_point_known():
    dp = calculate_dew_point(21, 40)
    assert 6.0 < dp < 8.0

def test_dew_point_high_humidity():
    dp = calculate_dew_point(21, 90)
    assert dp > 18.0


# --- Humidity score ---

def test_humidity_score_condensation():
    assert calculate_humidity_score(5.0, 10.0) == 0.0

def test_humidity_score_safe():
    assert calculate_humidity_score(15.0, 8.0) == 100.0

def test_humidity_score_marginal():
    score = calculate_humidity_score(10.0, 7.0)
    assert 0.0 < score < 100.0


# --- Air tightness ---

def test_air_tightness_no_draft():
    assert calculate_air_tightness_score(0.1) == 100.0

def test_air_tightness_severe_draft():
    assert calculate_air_tightness_score(1.5) == 0.0

def test_air_tightness_moderate():
    score = calculate_air_tightness_score(0.5)
    assert 0.0 < score < 100.0


# --- Wind heat loss factor ---

def test_wind_factor_calm():
    assert calculate_wind_heat_loss_factor(0.0) == 1.0

def test_wind_factor_windy():
    factor = calculate_wind_heat_loss_factor(5.0)
    assert factor > 1.0


# --- Overall efficiency ---

def test_overall_efficiency_perfect():
    score = calculate_overall_efficiency(100, 100, 100, 1.0)
    assert score == 100.0

def test_overall_efficiency_worst():
    score = calculate_overall_efficiency(0, 0, 0, 1.0)
    assert score == 0.0

def test_overall_efficiency_wind_penalty():
    no_wind = calculate_overall_efficiency(80, 80, 80, 1.0)
    windy = calculate_overall_efficiency(80, 80, 80, 2.0)
    assert windy < no_wind


# --- Energy waste ---

def test_energy_waste_calculation():
    kwh = estimate_energy_waste_kwh(u_value=3.0, area_m2=2.0, delta_t=10.0, hours=24)
    assert kwh == pytest.approx(1.44)


# --- Mock sensor data ---

def test_mock_sensor_data_ranges():
    for _ in range(20):
        data = generate_mock_sensor_data()
        assert 5.0 <= data["temp_glass"] <= 18.0
        assert 18.0 <= data["temp_amb"] <= 23.0
        assert 0.0 <= data["air_sensor"] <= 1.5


# --- Full assessment ---

def test_full_assessment_returns_all_keys():
    result = run_full_assessment(
        temp_outside=8, wind_speed_ms=3, humidity=70,
        temp_glass=12, temp_amb=21, air_sensor=0.3, window_area=1.5,
    )
    expected_keys = {
        "surface_temp_index", "u_value", "thermal_score", "dew_point",
        "humidity_score", "air_tightness_score", "wind_factor",
        "overall_efficiency", "energy_waste_kwh_per_day", "delta_t",
    }
    assert set(result.keys()) == expected_keys
    assert 0 <= result["overall_efficiency"] <= 100


# --- Weather service (mocked) ---

def test_fetch_weather_success():
    mock_json = {
        "name": "London",
        "main": {"temp": 12.5, "humidity": 65, "feels_like": 10.2},
        "wind": {"speed": 4.1},
        "weather": [{"description": "overcast clouds"}],
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_json

    with patch("weather_service.requests.get", return_value=mock_resp):
        result = fetch_weather_by_postcode("SW1A1AA", "fake_key")
        assert result["city_name"] == "London"
        assert result["temp_outside"] == 12.5
        assert result["wind_speed"] == 4.1


def test_fetch_weather_invalid_key():
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    with patch("weather_service.requests.get", return_value=mock_resp):
        with pytest.raises(WeatherAPIError, match="Invalid API key"):
            fetch_weather_by_postcode("SW1A1AA", "bad_key")


def test_fetch_weather_not_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch("weather_service.requests.get", return_value=mock_resp):
        with pytest.raises(WeatherAPIError, match="No weather data found"):
            fetch_weather_by_postcode("INVALID", "fake_key")


# --- API endpoints ---

def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@patch("main.fetch_weather_by_postcode")
def test_weather_endpoint(mock_weather):
    mock_weather.return_value = {
        "city_name": "London", "temp_outside": 10,
        "humidity": 80, "wind_speed": 3.5,
        "description": "rain", "feels_like": 7,
    }
    resp = client.get("/api/weather/SW1A1AA")
    assert resp.status_code == 200
    assert resp.json()["city_name"] == "London"


@patch("main.fetch_weather_by_postcode")
def test_calculate_endpoint(mock_weather):
    mock_weather.return_value = {
        "city_name": "London", "temp_outside": 10,
        "humidity": 80, "wind_speed": 3.5,
        "description": "rain", "feels_like": 7,
    }
    payload = {
        "name": "Jas",
        "postcode": "SW1A1AA",
        "property_type": "house",
        "window_type": "double-glazed",
        "window_height": 1.2,
        "window_width": 0.8,
        "has_sensor": False,
    }
    resp = client.post("/api/calculate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"] == "Jas"
    assert 0 <= body["results"]["overall_efficiency"] <= 100
