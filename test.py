import math

# Inputs (Sensor Data)
tempGlass = 10      # °C
tempAmb = 21        # °C
tempOutside = 12    # °C
humidity = 40       # % Relative Humidity
airSensor = 0.5     # Air velocity near frame in m/s (e.g., 0.1 m/s = minimal draft)
windSpeed = 30      # Outdoor wind speed in km/h
name = "Jas"
                                         
# Threshold Check
deltaT_overall = tempAmb - tempOutside

if deltaT_overall < 5:
    print("Warning: Temperature difference is too small for an accurate thermal reading.")
else:
    print("Sufficient ΔT for measurement.")

# --- 1. THERMAL SCORE (U-Value & Surface Index) ---
# Surface temperature index (0 to 1)
ft = (tempGlass - tempOutside) / (tempAmb - tempOutside)
ft = max(0.0, min(1.0, ft))  # Clamp between 0 and 1

# Heat Transfer Coefficient Calculations
# Standard indoor convective + radiative transfer coefficient h_i ≈ 7.7 W/m²K
h_i = 7.7 
u_value = h_i * (1.0 - ft)  # Estimated U-value (W/m²K)

# Convert U-value to a 0-100 score:
# Single glazing ≈ 5.8 W/m²K (Score 0) | Modern Triple Glazing ≤ 0.8 W/m²K (Score 100)
u_min, u_max = 0.8, 5.8
thermal_score = max(0.0, min(100.0, 100.0 * (u_max - u_value) / (u_max - u_min)))

# --- 2. CONDENSATION & HUMIDITY SCORE ---
# Calculate Dew Point using Magnus Formula
a, b = 17.27, 237.7
alpha = ((a * tempAmb) / (b + tempAmb)) + math.log(humidity / 100.0)
dew_point = (b * alpha) / (a - alpha)

# Condensation margin (difference between glass temperature and dew point)
margin = tempGlass - dew_point

if margin <= 0:
    humidity_score = 0.0  # Condensation present!
elif margin >= 5:
    humidity_score = 100.0  # Safe margin
else:
    humidity_score = (margin / 5.0) * 100.0

# --- 3. AIR TIGHTNESS SCORE ---
# Air leakage draft penalty based on air sensor reading (m/s)
# Comfort threshold: velocity < 0.15 m/s is acceptable, > 1.0 m/s is severe draft
if airSensor <= 0.15:
    air_score = 100.0
elif airSensor >= 1.0:
    air_score = 0.0
else:
    air_score = 100.0 * (1.0 - (airSensor - 0.15) / (1.0 - 0.15))

# --- 4. COMPOSITE OVERALL EFFICIENCY SCORE ---
# Weighted distribution: 50% Thermal, 30% Condensation Risk, 20% Air Tightness
w_thermal = 0.50
w_humidity = 0.30
w_air = 0.20

overall_eff = (w_thermal * thermal_score) + (w_humidity * humidity_score) + (w_air * air_score)

# --- RESULTS DISPLAY ---
print("\n--- Diagnostic Breakdown ---")
print(f"Window Owner: {name}")
print(f"Surface Temp Index (f_t): {ft:.2f}")
print(f"Estimated U-Value: {u_value:.2f} W/m²K")
print(f"Dew Point: {dew_point:.1f}°C (Glass Temp: {tempGlass}°C)")
print(f"Thermal Score: {thermal_score:.1f}/100")
print(f"Humidity/Condensation Score: {humidity_score:.1f}/100")
print(f"Air Tightness Score: {air_score:.1f}/100")
print(f"Overall Efficiency Score: {overall_eff:.1f}/100")