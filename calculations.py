#Calculatoins to for the efficiency score featured for each window featured on the app 


#pulls the data from the hardware devices (but for now keep it as regular variables)
tempGlass = 10
tempAmb = 21
humidity = 40
airSensor = 5
windSpeed = 30
tempOutside = 12
name = "Jas"

#surface temperature index
ft = (tempGlass - tempOutside)/(tempAmb - tempOutside)
deltaT_overall = tempAmb - tempOutside
deltaT_surface = tempAmb - tempGlass

#sensible winter heat loss conditions 
if tempAmb > tempGlass > tempOutside: 

#sensible summer heat gain conditions


if deltaT_overall >= 10:
    print("Good conditions for measurement!")

else:
    print("Temperature difference is too small for accurate measurement.")


#heat transfer estimates

# --- 4. COMPOSITE OVERALL EFFICIENCY SCORE ---
# Weighted distribution: 50% Thermal, 30% Condensation Risk, 20% Air Tightness
w_thermal = 0.50
w_humidity = 0.30
w_air = 0.20

overall_eff = (w_thermal * thermal_score) + (w_humidity * humidity_score) + (w_air * air_score)


#efficiency score
eff = 100*ft
if eff < 0 or eff >100:
    print("Error: Efficiency score is out of bounds. Please check the input values.")
else:
    print(f"the efficiency of {name} window is {eff}")




