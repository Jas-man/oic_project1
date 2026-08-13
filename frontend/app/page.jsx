"use client";

import { useState } from "react";
import styles from "./page.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function ScoreGauge({ score, label }) {
  let color = "#e74c3c";
  if (score >= 70) color = "#27ae60";
  else if (score >= 40) color = "#f39c12";

  return (
    <div className={styles.gauge}>
      <div className={styles.gaugeCircle} style={{ borderColor: color }}>
        <span className={styles.gaugeValue} style={{ color }}>
          {score}
        </span>
      </div>
      <span className={styles.gaugeLabel}>{label}</span>
    </div>
  );
}

function ScoreCard({ title, score, description }) {
  let bg = "#fdecea";
  if (score >= 70) bg = "#e8f5e9";
  else if (score >= 40) bg = "#fff8e1";

  return (
    <div className={styles.scoreCard} style={{ backgroundColor: bg }}>
      <h3>{title}</h3>
      <span className={styles.scoreValue}>{score}/100</span>
      <p>{description}</p>
    </div>
  );
}

function getInterpretation(results) {
  const messages = [];
  if (results.thermal_score < 40)
    messages.push(
      "Your windows have poor thermal insulation — consider upgrading to double or triple glazing."
    );
  if (results.humidity_score < 40)
    messages.push(
      "High condensation risk detected. Improve ventilation or check window seals."
    );
  if (results.air_tightness_score < 40)
    messages.push(
      "Significant air leakage around your window frames. Re-sealing may help."
    );
  if (results.wind_factor > 2.0)
    messages.push(
      "High wind exposure is increasing heat loss through your windows."
    );
  if (messages.length === 0)
    messages.push("Your windows are performing well in current conditions.");
  return messages;
}

export default function Home() {
  const [formData, setFormData] = useState({
    name: "",
    postcode: "",
    property_type: "house",
    window_type: "double-glazed",
    window_height: "",
    window_width: "",
    has_sensor: false,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await fetch(`${API_BASE}/api/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          window_height: parseFloat(formData.window_height),
          window_width: parseFloat(formData.window_width),
        }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Server error (${resp.status})`);
      }
      setResult(await resp.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>WESH</h1>
        <p>Live Window Efficiency Score Calculator</p>
      </header>

      <main className={styles.main}>
        <form className={styles.form} onSubmit={handleSubmit}>
          <h2>Your Details</h2>

          <label>
            Name
            <input
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            UK Postcode
            <input
              name="postcode"
              value={formData.postcode}
              onChange={handleChange}
              placeholder="e.g. SW1A 1AA"
              required
            />
          </label>

          <label>
            Property Type
            <select
              name="property_type"
              value={formData.property_type}
              onChange={handleChange}
            >
              <option value="house">House</option>
              <option value="flat">Flat</option>
              <option value="business">Business</option>
            </select>
          </label>

          <label>
            Window Type
            <select
              name="window_type"
              value={formData.window_type}
              onChange={handleChange}
            >
              <option value="single-glazed">Single Glazed</option>
              <option value="double-glazed">Double Glazed</option>
              <option value="triple-glazed">Triple Glazed</option>
              <option value="idk">I don&apos;t know</option>
            </select>
          </label>

          <div className={styles.row}>
            <label>
              Window Height (m)
              <input
                name="window_height"
                type="number"
                step="0.01"
                min="0.1"
                value={formData.window_height}
                onChange={handleChange}
                required
              />
            </label>
            <label>
              Window Width (m)
              <input
                name="window_width"
                type="number"
                step="0.01"
                min="0.1"
                value={formData.window_width}
                onChange={handleChange}
                required
              />
            </label>
          </div>

          <label className={styles.checkbox}>
            <input
              name="has_sensor"
              type="checkbox"
              checked={formData.has_sensor}
              onChange={handleChange}
            />
            I have a WESH sensor installed
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Calculating..." : "Calculate Efficiency"}
          </button>
        </form>

        {error && <div className={styles.error}>{error}</div>}

        {result && (
          <section className={styles.results}>
            <h2>Results for {result.user}</h2>

            <div className={styles.weatherCard}>
              <h3>
                Weather in {result.weather.city_name}
              </h3>
              <div className={styles.weatherGrid}>
                <div>
                  <span className={styles.weatherValue}>
                    {result.weather.temp_outside}°C
                  </span>
                  <span>Temperature</span>
                </div>
                <div>
                  <span className={styles.weatherValue}>
                    {result.weather.wind_speed} m/s
                  </span>
                  <span>Wind Speed</span>
                </div>
                <div>
                  <span className={styles.weatherValue}>
                    {result.weather.humidity}%
                  </span>
                  <span>Humidity</span>
                </div>
                <div>
                  <span className={styles.weatherValue}>
                    {result.weather.description}
                  </span>
                  <span>Conditions</span>
                </div>
              </div>
            </div>

            <div className={styles.overallSection}>
              <ScoreGauge
                score={result.results.overall_efficiency}
                label="Overall Efficiency"
              />
              <div className={styles.energyWaste}>
                <h3>Estimated Energy Waste</h3>
                <span className={styles.energyValue}>
                  {result.results.energy_waste_kwh_per_day} kWh/day
                </span>
                <p>
                  Through {result.window_area_m2} m² of window area (ΔT:{" "}
                  {result.results.delta_t}°C)
                </p>
                <p className={styles.uValue}>
                  Estimated U-Value: {result.results.u_value} W/m²K
                </p>
              </div>
            </div>

            <div className={styles.scoreGrid}>
              <ScoreCard
                title="Thermal"
                score={result.results.thermal_score}
                description={`Surface temp index: ${result.results.surface_temp_index}`}
              />
              <ScoreCard
                title="Condensation Risk"
                score={result.results.humidity_score}
                description={`Dew point: ${result.results.dew_point}°C`}
              />
              <ScoreCard
                title="Air Tightness"
                score={result.results.air_tightness_score}
                description={`Wind factor: ${result.results.wind_factor}x`}
              />
            </div>

            <div className={styles.interpretation}>
              <h3>Recommendations</h3>
              <ul>
                {getInterpretation(result.results).map((msg, i) => (
                  <li key={i}>{msg}</li>
                ))}
              </ul>
            </div>

            {!result.sensor_data && (
              <p className={styles.sensorNote}>
                Sensor data is simulated. Install a WESH sensor for real
                readings.
              </p>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
