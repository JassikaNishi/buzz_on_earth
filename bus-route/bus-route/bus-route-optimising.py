import pandas as pd

# Load the dataset from the CSV file
df = pd.read_csv(r'bus-route\bus_routes_python_dataset.csv')

# Function to get route information based on user input
def get_route_info(from_location, to_location):
    # Convert user input and dataset columns to lowercase for case-insensitive comparison
    from_location = from_location.lower()
    to_location = to_location.lower()
    
    # Filter the dataset based on the selected locations (also converted to lowercase)
    route_info = df[(df['From Location'].str.lower() == from_location) & 
                    (df['To Location'].str.lower() == to_location)]
    
    if route_info.empty:
        return "No route found for the given locations."
    
    return route_info

# Function to recommend the best bus type based on cost, emissions, and other factors
def recommend_bus(from_location, to_location):
    route_info = get_route_info(from_location, to_location)
    
    if isinstance(route_info, str):
        return route_info  # If no route found, return message
    
    # Extract the best recommendation based on cost and emissions
    recommendation = route_info.sort_values(by=['Operational Cost (USD/km)', 'Emissions (g CO2/km)']).iloc[0]
    return recommendation, route_info

# Function to calculate total cost and total time taken
def calculate_travel_details(route_info, distance):
    # Assuming 'Operational Cost (USD/km)' and 'Avg Speed (km/h)' are present in the route_info
    operational_cost_per_km = route_info['Operational Cost (USD/km)']  # Access directly
    avg_speed = route_info['Avg Speed (km/h)']  # Access directly

    # Calculate total cost
    total_cost = operational_cost_per_km * distance

    # Calculate total time taken in hours
    total_time_hours = distance / avg_speed  # Time = Distance / Speed
    
    # Convert total time into hours and minutes
    hours = int(total_time_hours)  # Get whole hours
    minutes = int((total_time_hours - hours) * 60)  # Convert remaining fraction to minutes

    return total_cost, hours, minutes

# Get user input for locations
print("Enter the following details to get the route information and recommended bus type:")

from_location = input("From Location (North Park/South Valley/West End/East Side/Central Station): ")
to_location = input("To Location (North Park/South Valley/West End/East Side/Central Station): ")

# Get the recommended bus type and route info based on user input
recommended_bus, route_info = recommend_bus(from_location, to_location)

if isinstance(route_info, str):
    print(route_info)  # Print the error message if no route found
else:
    print(f"\nRoute Information from {from_location} to {to_location}:\n{route_info}")

    # Extract distance from route info
    distance = route_info['Distance (km)'].values[0]

    # Calculate total cost and total time taken
    total_cost, total_hours, total_minutes = calculate_travel_details(route_info.iloc[0], distance)

    print(f"\nRecommended bus type: {recommended_bus['Bus Type']}")
    print(f"Total Cost of Travel: ${total_cost:.2f}")
    print(f"Total Time Taken: {total_hours} hours and {total_minutes} minutes")
