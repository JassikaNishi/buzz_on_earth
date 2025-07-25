from flask import Flask, render_template, request
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load dataset and model
df = pd.read_csv(r"C:\Users\jassika\OneDrive\Desktop\Katoch's model\travell-pattern\travell-pattern\week_bus_departure_data.csv")
model_path = r"C:\Users\jassika\OneDrive\Desktop\Katoch's model\travell-pattern\travell-pattern\crowd_forecast_model.pkl"

# Convert 'Departure Time' to datetime objects
df['Departure Time'] = pd.to_datetime(df['Departure Time'])

# Get unique locations for the dropdown menu
locations = df['Departure Location'].unique()

# Route for homepage with form
@app.route('/')
def index():
    return render_template('index.html', locations=locations)

# Route for handling form submission
@app.route('/predict', methods=['POST'])
def predict():
    # Get selected location from the form
    selected_location = request.form.get('location')

    # Filter the data for the selected location
    location_data = df[df['Departure Location'] == selected_location]
    location_data.set_index('Departure Time', inplace=True)
    
    # Resample the data to hourly frequency
    hourly_data = location_data.resample('H').sum().fillna(0)

    # Load the pre-trained SARIMA model
    model = joblib.load(model_path)
    
    # Forecast for the next 24 hours
    future_forecast = model.forecast(steps=24)
    future_forecast = np.clip(future_forecast, 0, None)  # Ensure non-negative values
    
    # Create a time index for the next 24 hours
    future_index = pd.date_range(start=hourly_data.index[-1] + pd.Timedelta(hours=1), periods=24, freq='H')
    
    # Plotting the forecast
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(future_index, future_forecast, label=f'Forecast - {selected_location}', linestyle='-', color='b')
    ax.set_title(f'Future Crowd Size Predictions for {selected_location}', fontsize=16)
    ax.set_xlabel('Time (Next 24 Hours)', fontsize=14)
    ax.set_ylabel('Predicted Crowd Size', fontsize=14)
    ax.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    
    # Save the plot to a string buffer in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('result.html', location=selected_location, plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
