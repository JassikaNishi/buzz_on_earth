import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np
import pickle

# Load the dataset
df = pd.read_csv(r"C:\Users\jassika\OneDrive\Desktop\Katoch's model\travell-pattern\travell-pattern\week_bus_departure_data.csv")

# Convert 'Departure Time' to datetime objects
df['Departure Time'] = pd.to_datetime(df['Departure Time'])

# Sum the crowd size at each location
crowd_summary = df.groupby('Departure Location')['Crowd Size'].sum().reset_index()

# Get unique locations
locations = df['Departure Location'].unique()

# Print valid locations for reference
print("Available locations:", locations)

# Choose a specific location (replace 'some_location' with a valid location from your dataset)
user_input = "East side"  # Example: replace this with an actual location name from the printed list

# Check if the input location is valid
if user_input not in locations:
    print(f"Location '{user_input}' not found in the dataset.")
else:
    # Filter data for the specified location
    location_data = df[df['Departure Location'] == user_input]

    # Set 'Departure Time' as index for time series analysis
    location_data.set_index('Departure Time', inplace=True)

    # Resampling to hourly frequency (in case there's missing data)
    hourly_data = location_data.resample('H').sum().fillna(0)

    # Fit SARIMA model (Seasonal ARIMA)
    model = SARIMAX(hourly_data['Crowd Size'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 24))
    model_fit = model.fit(disp=False)

    # Save the trained model to a pickle file
    with open('sarima_model.pkl', 'wb') as f:
        pickle.dump(model_fit, f)

    print("Model saved successfully to 'sarima_model.pkl'")
