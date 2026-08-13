import math
import random


def calculate_surface_temp_index(temp_glass: float, temp_amb: float, temp_outside: float) -> float:
    delta = temp_amb - temp_outside
    if delta == 0:
        return 0.0
    ft = (temp_glass - temp_outside) / delta
    return max(0.0, min(1.0, ft))


# Standard indoor convective + radiative coefficient h_i ~ 7.7 W/m²K
H_I = 7.7

def estimate_u_value(ft: float, h_i: float = H_I) -> float:
    return h_i * (1.0 - ft)


# Single glazing ~ 5.8 W/m²K (score 0), modern triple glazing <= 0.8 W/m²K (score 100)
U_MIN, U_MAX = 0.8, 5.8

def calculate_thermal_score(u_value: float, u_min: float = U_MIN, u_max: float = U_MAX) -> float:
    return max(0.0, min(100.0, 100.0 * (u_max - u_value) / (u_max - u_min)))


def calculate_dew_point(temp_amb: float, humidity: float) -> float:
    a, b = 17.27, 237.7
    alpha = ((a * temp_amb) / (b + temp_amb)) + math.log(max(humidity, 0.1) / 100.0)
    return (b * alpha) / (a - alpha)


def calculate_humidity_score(temp_glass: float, dew_point: float) -> float:
    margin = temp_glass - dew_point
    if margin <= 0:
        return 0.0
    if margin >= 5:
        return 100.0
    return (margin / 5.0) * 100.0


def calculate_air_tightness_score(air_velocity: float) -> float:
    if air_velocity <= 0.15:
        return 100.0
    if air_velocity >= 1.0:
        return 0.0
    return 100.0 * (1.0 - (air_velocity - 0.15) / (1.0 - 0.15))


# BS EN ISO 6946: h_e ~ 5.8 + 3.95 * wind_speed (m/s)
H_E_STILL = 5.8

def calculate_wind_heat_loss_factor(wind_speed_ms: float) -> float:
    h_e = H_E_STILL + 3.95 * max(wind_speed_ms, 0.0)
    return h_e / H_E_STILL


W_THERMAL = 0.50
W_HUMIDITY = 0.30
W_AIR = 0.20

def calculate_overall_efficiency(
    thermal_score: float,
    humidity_score: float,
    air_score: float,
    wind_factor: float = 1.0,
) -> float:
    # Wind factor penalises the thermal component (more wind = more heat loss)
    adjusted_thermal = max(0.0, thermal_score / wind_factor)
    raw = (W_THERMAL * adjusted_thermal) + (W_HUMIDITY * humidity_score) + (W_AIR * air_score)
    return max(0.0, min(100.0, raw))


def estimate_energy_waste_kwh(u_value: float, area_m2: float, delta_t: float, hours: float = 24.0) -> float:
    watts = u_value * area_m2 * delta_t
    return (watts * hours) / 1000.0


def generate_mock_sensor_data() -> dict:
    return {
        "temp_glass": round(random.uniform(5.0, 18.0), 1),
        "temp_amb": round(random.uniform(18.0, 23.0), 1),
        "air_sensor": round(random.uniform(0.0, 1.5), 2),
    }


def run_full_assessment(
    temp_outside: float,
    wind_speed_ms: float,
    humidity: float,
    temp_glass: float,
    temp_amb: float,
    air_sensor: float,
    window_area: float,
) -> dict:
    ft = calculate_surface_temp_index(temp_glass, temp_amb, temp_outside)
    u_value = estimate_u_value(ft)
    thermal_score = calculate_thermal_score(u_value)

    dew_point = calculate_dew_point(temp_amb, humidity)
    humidity_score = calculate_humidity_score(temp_glass, dew_point)

    air_score = calculate_air_tightness_score(air_sensor)

    wind_factor = calculate_wind_heat_loss_factor(wind_speed_ms)

    overall = calculate_overall_efficiency(thermal_score, humidity_score, air_score, wind_factor)

    delta_t = temp_amb - temp_outside
    energy_waste = estimate_energy_waste_kwh(u_value, window_area, delta_t)

    return {
        "surface_temp_index": round(ft, 3),
        "u_value": round(u_value, 2),
        "thermal_score": round(thermal_score, 1),
        "dew_point": round(dew_point, 1),
        "humidity_score": round(humidity_score, 1),
        "air_tightness_score": round(air_score, 1),
        "wind_factor": round(wind_factor, 2),
        "overall_efficiency": round(overall, 1),
        "energy_waste_kwh_per_day": round(energy_waste, 2),
        "delta_t": round(delta_t, 1),
    }

