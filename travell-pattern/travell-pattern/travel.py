import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np
import joblib

# Load the dataset
df = pd.read_csv(r"C:\Users\jassika\OneDrive\Desktop\Katoch's model\travell-pattern\travell-pattern\week_bus_departure_data.csv")

# Convert 'Departure Time' to datetime objects
df['Departure Time'] = pd.to_datetime(df['Departure Time'])

# Sum the crowd size at each location
crowd_summary = df.groupby('Departure Location')['Crowd Size'].sum().reset_index()

# Print the crowd summary
print("Crowd Summary by Location:")
print(crowd_summary)

# Get unique locations
locations = df['Departure Location'].unique()

# Ask the user for a specific location
user_input = input("Enter a departure location to see its crowd size predictions: ")

# Check if the input location is valid
if user_input not in locations:
    print(f"Location '{user_input}' not found in the dataset. Please try again.")
else:
    # Assign a color for each location
    colors = sns.color_palette("husl", len(locations))  # Use Seaborn to generate distinct colors
    color_map = {location: colors[i] for i, location in enumerate(locations)}

    # Dictionary to store predictions for the specified location
    predictions = {}

    # Plotting and Forecasting for the specified location
    plt.figure(figsize=(12, 6))

    # Filter data for the specified location
    location_data = df[df['Departure Location'] == user_input]

    # Set 'Departure Time' as index for time series analysis
    location_data.set_index('Departure Time', inplace=True)

    # Resampling to hourly frequency (in case there's missing data)
    hourly_data = location_data.resample('H').sum().fillna(0)

    # Fit SARIMA model (Seasonal ARIMA)
    model = SARIMAX(hourly_data['Crowd Size'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 24))
    model_fit = model.fit(disp=False)

    # Forecast the next 24 hours
    future_forecast = model_fit.forecast(steps=24)

    # Ensure predictions are non-negative by applying a threshold
    future_forecast = np.clip(future_forecast, 0, None)

    # Store predictions in the dictionary for access
    predictions[user_input] = future_forecast

    # Create a time index for the forecast
    future_index = pd.date_range(start=hourly_data.index[-1] + pd.Timedelta(hours=1), periods=24, freq='H')

    # Plot only the future forecast
    plt.plot(future_index, future_forecast, label=f'Forecast - {user_input}', linestyle='-', color=color_map[user_input])

    # Customize the plot
    plt.title(f'Future Crowd Size Predictions for {user_input}', fontsize=16)
    plt.xlabel('Time (Next 24 Hours)', fontsize=14)
    plt.ylabel('Predicted Crowd Size', fontsize=14)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Show the plot
    plt.show()

    # Access and print the forecasted values
    print("Forecasted Crowd Sizes for the next 24 hours:")
    print(f"\nLocation: {user_input}")
    print(predictions[user_input])

    # Save the model correctly
    joblib.dump(model_fit, r"C:\Users\jassika\OneDrive\Desktop\Katoch's model\travell-pattern\travell-pattern\crowd_forecast_model.pkl")
    print("Model saved successfully!")
