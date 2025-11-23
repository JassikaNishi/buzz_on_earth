from flask import Flask, render_template, request
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# BASE DIRECTORY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------
# CROWD MODEL
# -------------------------------
MODEL_PATH = os.path.join(BASE_DIR, "..", "travell-pattern", "travell-pattern", "crowd_forecast_model.pkl")
CSV_PATH = os.path.join(BASE_DIR, "..", "travell-pattern", "travell-pattern", "week_bus_departure_data.csv")

model = joblib.load(MODEL_PATH)
df = pd.read_csv(CSV_PATH)
df['Departure Time'] = pd.to_datetime(df['Departure Time'])

# -------------------------------
# ROUTE DATA
# -------------------------------
ROUTE_CSV = os.path.join(BASE_DIR, "..", "bus-route", "bus-route", "bus_routes_python_dataset.csv")
route_df = pd.read_csv(ROUTE_CSV)

# -------------------------------
# MAINTENANCE DATA
# -------------------------------
MAINTENANCE_CSV = os.path.join(BASE_DIR, "..", "maintenance", "maintenance", "bus_maintenance_data.csv")
maintenance_df = pd.read_csv(MAINTENANCE_CSV)


# ==============================
# CROWD FORECAST PAGE
# ==============================
@app.route('/crowd', methods=["GET", "POST"])
def crowd_page():
    locations = df["Departure Location"].unique()
    forecast_list = None
    selected_location = None

    if request.method == "POST":
        selected_location = request.form["location"]

        data = df[df['Departure Location'] == selected_location].copy()
        data.set_index('Departure Time', inplace=True)
        hourly_data = data.resample('H').sum().fillna(0)

        forecast = model.forecast(steps=24)
        forecast_list = list(np.clip(forecast, 0, None))

    return render_template("crowd.html",
                           locations=locations,
                           forecast=forecast_list,
                           location=selected_location
                           )


# ==============================
# ROUTE OPTIMISATION PAGE
# ==============================
def get_route_info(from_location, to_location):
    return route_df[
        (route_df["From Location"].str.lower() == from_location.lower()) &
        (route_df["To Location"].str.lower() == to_location.lower())
    ]

def recommend_bus(df_temp):
    if df_temp.empty:
        return None
    return df_temp.sort_values(
        by=["Operational Cost (USD/km)", "Emissions (g CO2/km)"]
    ).iloc[0]

@app.route('/route', methods=['GET', 'POST'])
def route_page():
    result = None
    error = None
    locations = sorted(route_df["From Location"].unique())

    if request.method == "POST":
        from_loc = request.form["from_loc"]
        to_loc = request.form["to_loc"]

        df_temp = get_route_info(from_loc, to_loc)

        if df_temp.empty:
            error = "No route found matching your selection."
        else:
            best = recommend_bus(df_temp)
            distance = best["Distance (km)"]

            cost = round(best["Operational Cost (USD/km)"] * distance, 2)

            hours = distance / best["Avg Speed (km/h)"]
            h = int(hours)
            m = int((hours - h) * 60)

            result = type("Result", (), {
                "best_bus": best["Bus Type"],
                "distance": distance,
                "cost": cost,
                "time_h": h,
                "time_m": m
            })

    return render_template("route.html",
                           locations=locations,
                           result=result,
                           error=error)


# ==============================
# MAINTENANCE PAGE
# ==============================
MAINTENANCE_INTERVAL_KM = 75000
MAINTENANCE_INTERVAL_DAYS = 700
BREAKDOWN_THRESHOLD = 2
DOWNTIME_THRESHOLD = 20
DRIVER_BEHAVIOR_THRESHOLD = 70

def maintenance_status(row):
    last_maint = pd.to_datetime(row["Last Maintenance Date"])
    days_since = (datetime.now() - last_maint).days

    mileage_since = row["Mileage (km)"] % MAINTENANCE_INTERVAL_KM
    km_left = MAINTENANCE_INTERVAL_KM - mileage_since
    days_left = MAINTENANCE_INTERVAL_DAYS - days_since

    status = "On Schedule"
    next_date = datetime.now().date()

    if (days_since >= MAINTENANCE_INTERVAL_DAYS or
        mileage_since >= MAINTENANCE_INTERVAL_KM or
        row["Breakdowns (last year)"] > BREAKDOWN_THRESHOLD or
        row["Downtime (days)"] > DOWNTIME_THRESHOLD or
        row["Driver Behavior Score (out of 100)"] < DRIVER_BEHAVIOR_THRESHOLD):
        status = "Due Now"

    return status, str(next_date)[:10], days_since, mileage_since, km_left, days_left


@app.route("/maintenance", methods=["GET", "POST"])
def maintenance_page():
    bus_ids = maintenance_df["Bus_ID"].unique()
    result = None

    if request.method == "POST":
        selected_id = request.form["bus_id"]
        row = maintenance_df[maintenance_df["Bus_ID"] == selected_id].iloc[0]

        status, next_date, days_since, mileage_since, km_left, days_left = maintenance_status(row)

        result = {
            "bus_id": selected_id,
            "status": status,
            "next_date": next_date,
            "days_since": days_since,
            "mileage_since": mileage_since,
            "km_left": km_left,
            "days_left": days_left,
            "breakdowns": row["Breakdowns (last year)"],
            "downtime": row["Downtime (days)"],
            "driver_score": row["Driver Behavior Score (out of 100)"]
        }

    return render_template("maintenance.html", bus_ids=bus_ids, result=result)


# ==============================
# DASHBOARD
# ==============================
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
