import csv

# Dataset as a list of dictionaries
data = [
    {'From Location': 'North Park', 'To Location': 'Central Station', 'Route Type': 'Urban', 'Bus Type': 'Electric', 'Distance (km)': 10, 'Stops': 15, 'Terrain': 'Flat', 'Fuel Efficiency (km/l)': None, 'Emissions (g CO2/km)': 0, 'Operational Cost (USD/km)': 0.10, 'Avg Speed (km/h)': 35},
    {'From Location': 'South Valley', 'To Location': 'North Park', 'Route Type': 'Suburban', 'Bus Type': 'Diesel', 'Distance (km)': 30, 'Stops': 12, 'Terrain': 'Hilly', 'Fuel Efficiency (km/l)': 6.2, 'Emissions (g CO2/km)': 140, 'Operational Cost (USD/km)': 0.14, 'Avg Speed (km/h)': 50},
    #... (continue for all routes)
]

# Writing the data to a CSV file
with open('bus_routes_python_dataset.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("Data has been successfully written to bus_routes_python_dataset.csv")
