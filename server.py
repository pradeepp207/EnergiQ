from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import math

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────
#  Simulated building state
# ─────────────────────────────────────────
state = {
    "solar_kw":        8.4,
    "battery_pct":     72.0,
    "grid_kw":         2.1,
    "demand_kw":       10.5,
    "ev_charging":     True,
    "ev_delay_min":    0,
    "water_pump":      True,
    "ac_kw":           5.0,
    "computer_lab_kw": 3.0,
    "lighting_kw":     1.2,
    "server_kw":       0.8,
    # Manual overrides
    "manual_electricity_kwh": 0.0,
    "manual_water_liters":    0.0,
}

decisions_log = []

# ─────────────────────────────────────────
#  AI Decision Engine
# ─────────────────────────────────────────
def run_ai_engine():
    global state
    decisions = []
    savings_inr = 0.0
    solar_util  = 0.0
    grid_saved  = 0.0

    solar   = state["solar_kw"]
    battery = state["battery_pct"]
    demand  = state["demand_kw"]
    hour    = datetime.now().hour

    # Predict solar increase (simplified)
    solar_rising = (hour >= 8 and hour <= 13)
    solar_falling = (hour >= 14 and hour <= 18)
    tariff_high = (hour >= 9 and hour <= 11) or (hour >= 18 and hour <= 21)

    surplus = solar - demand

    if surplus > 2:
        decisions.append({
            "action":  "Charging battery from solar surplus",
            "reason":  f"Solar surplus of {surplus:.1f} kW — storing energy for later use",
            "savings": f"₹{surplus * 8:.0f} estimated savings",
            "icon":    "🔋"
        })
        solar_util += surplus
        savings_inr += surplus * 8

    if tariff_high and battery > 30:
        decisions.append({
            "action":  "Switching to battery power for flexible loads",
            "reason":  "Grid tariff is currently high — using stored energy instead",
            "savings": f"₹{demand * 0.3 * 6:.0f} peak-hour savings",
            "icon":    "💰"
        })
        savings_inr += demand * 0.3 * 6

    if solar_rising and state["ev_charging"]:
        state["ev_delay_min"] = 35
        decisions.append({
            "action":  "EV charging delayed by 35 minutes",
            "reason":  "Solar generation predicted to rise 22% within the hour",
            "savings": "₹18 estimated saving on grid import",
            "icon":    "🚗"
        })
        savings_inr += 18
        grid_saved  += 4.0

    if solar_falling and battery < 50:
        decisions.append({
            "action":  "Preserving battery reserve — 70% floor set",
            "reason":  "Solar generation will drop after 4 PM; maintaining backup capacity",
            "savings": "Ensures 2 hrs uninterrupted critical-load power",
            "icon":    "⚡"
        })

    if demand > solar + (battery / 100 * 20):
        decisions.append({
            "action":  "Load-shedding non-critical flexible loads",
            "reason":  "Combined solar + battery insufficient; reducing flexible demand",
            "savings": "Avoids grid peak-demand surcharge",
            "icon":    "🌿"
        })

    health_score = min(100, max(0,
        60 +
        (solar / 15 * 20) +
        (battery / 100 * 10) +
        (10 if not tariff_high else 0)
    ))

    return {
        "decisions":    decisions,
        "savings_inr":  round(savings_inr, 2),
        "solar_util_kwh": round(solar_util, 2),
        "grid_saved_kwh": round(grid_saved, 2),
        "health_score": round(health_score, 1),
        "tariff_high":  tariff_high,
    }

# ─────────────────────────────────────────
#  Solar forecast (next 6 hours)
# ─────────────────────────────────────────
def get_forecast():
    now = datetime.now()
    forecast = []
    for i in range(7):
        t = now + timedelta(hours=i)
        h = t.hour
        # Simple bell curve solar model
        solar = max(0, 12 * math.sin(math.pi * (h - 6) / 12)) if 6 <= h <= 18 else 0
        solar += random.uniform(-0.5, 0.5)
        demand = 8 + 2 * math.sin(math.pi * (h - 8) / 10) + random.uniform(-0.3, 0.3)
        forecast.append({
            "time":   t.strftime("%I %p"),
            "solar":  round(max(0, solar), 1),
            "demand": round(max(4, demand), 1),
        })
    return forecast

# ─────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────
@app.route("/status", methods=["GET"])
def get_status():
    # Simulate live fluctuation
    state["solar_kw"]    = round(max(0, state["solar_kw"]    + random.uniform(-0.3, 0.3)), 2)
    state["battery_pct"] = round(min(100, max(0, state["battery_pct"] + random.uniform(-0.5, 0.8))), 1)
    state["grid_kw"]     = round(max(0, state["grid_kw"]     + random.uniform(-0.2, 0.2)), 2)
    state["demand_kw"]   = round(max(5, state["demand_kw"]   + random.uniform(-0.4, 0.4)), 2)

    ai = run_ai_engine()

    return jsonify({
        **state,
        **ai,
        "forecast":  get_forecast(),
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    action = data.get("action")
    value  = data.get("value")

    responses = {
        "ev_on":        lambda: state.update({"ev_charging": True}),
        "ev_off":       lambda: state.update({"ev_charging": False}),
        "pump_on":      lambda: state.update({"water_pump": True}),
        "pump_off":     lambda: state.update({"water_pump": False}),
        "ac_increase":  lambda: state.update({"ac_kw": min(10, state["ac_kw"] + 0.5)}),
        "ac_decrease":  lambda: state.update({"ac_kw": max(0, state["ac_kw"] - 0.5)}),
    }

    if action in responses:
        responses[action]()
        return jsonify({"ok": True, "message": f"Command '{action}' applied"})

    return jsonify({"ok": False, "message": "Unknown command"}), 400

@app.route("/manual", methods=["POST"])
def manual_input():
    data = request.json
    kwh    = float(data.get("electricity_kwh", 0))
    liters = float(data.get("water_liters", 0))

    state["manual_electricity_kwh"] += kwh
    state["manual_water_liters"]    += liters

    # Adjust demand based on manual electricity input
    if kwh > 0:
        state["demand_kw"] = round(state["demand_kw"] + (kwh * 0.1), 2)

    return jsonify({
        "ok": True,
        "message": f"Logged {kwh} kWh electricity and {liters} L water",
        "totals": {
            "electricity_kwh": state["manual_electricity_kwh"],
            "water_liters":    state["manual_water_liters"],
        }
    })

@app.route("/reset_manual", methods=["POST"])
def reset_manual():
    state["manual_electricity_kwh"] = 0.0
    state["manual_water_liters"]    = 0.0
    return jsonify({"ok": True, "message": "Manual readings reset"})

if __name__ == "__main__":
    app.run(debug=True, port=8000)