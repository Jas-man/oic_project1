# WESH — Live Window Efficiency Score Calculator

A web application that uses live UK weather data to calculate the thermal efficiency of your windows and estimate energy waste.

## Prerequisites

- Python 3.10+
- Node.js 18+
- An [OpenWeather API key](https://home.openweathermap.org/users/sign_up) (free tier)

## Backend Setup

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # bash/zsh
source venv/bin/activate.fish   # fish shell

# Install dependencies
pip install -r requirements.txt

# Add your OpenWeather API key
echo "WEATHER_API_KEY=your_key_here" > .env

# Run the API server
uvicorn main:app --reload
```

The API will be available at http://localhost:8000. Verify with http://localhost:8000/api/health.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser.

## Running Tests

```bash
source venv/bin/activate
python -m pytest test.py -v
```

## Project Structure

```
├── main.py              # FastAPI server with /api/calculate, /api/weather, /api/health
├── calculations.py      # Pure functions for thermal, humidity, air tightness scoring
├── weather_service.py   # OpenWeather API client (UK postcodes, metric units)
├── test.py              # pytest suite (31 tests)
├── requirements.txt     # Python dependencies
├── .env                 # Your API key (not committed)
└── frontend/            # Next.js app
    └── app/
        ├── layout.js
        ├── page.jsx     # Input form + results dashboard
        ├── page.module.css
        └── globals.css
```

## How It Works

1. Enter your name, UK postcode, property type, and window dimensions
2. The backend fetches live weather data (temperature, wind speed, humidity) from OpenWeather
3. Sensor readings are simulated with realistic values (until a WESH hardware sensor is connected)
4. The app calculates:
   - **Thermal Score** — based on estimated U-value from surface temperature index
   - **Condensation Risk** — dew point vs glass temperature
   - **Air Tightness** — draft detection from air velocity sensor
   - **Wind Factor** — external heat transfer coefficient adjusted for wind speed (BS EN ISO 6946)
   - **Overall Efficiency** — weighted composite (50% thermal, 30% humidity, 20% air tightness)
   - **Energy Waste** — estimated kWh lost per day through the window
