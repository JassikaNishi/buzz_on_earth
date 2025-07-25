import pandas as pd
from datetime import datetime, timedelta
df = pd.read_csv('maintenance/bus_maintenance_data.csv')

# Set updated thresholds
MAINTENANCE_INTERVAL_KM = 75000  # Maintenance required every 75,000 km
MAINTENANCE_INTERVAL_DAYS = 700   # Maintenance required every 700 days (approximately 2 years)
BREAKDOWN_THRESHOLD = 2            # More than 2 breakdowns in the last year
DOWNTIME_THRESHOLD = 20            # Downtime exceeds 20 days
DRIVER_BEHAVIOR_THRESHOLD = 70     # Driver behavior score less than 70

# Function to check when maintenance is due
def calculate_maintenance_due(row):
    # Convert last maintenance date to datetime
    last_maintenance_date = pd.to_datetime(row['Last Maintenance Date'])
    
    # Calculate time since last maintenance
    days_since_last_maintenance = (datetime.now() - last_maintenance_date).days
    
    # Calculate mileage since last maintenance
    mileage_since_last_maintenance = row['Mileage (km)'] % MAINTENANCE_INTERVAL_KM
    
    # Calculate total distance driven since the last maintenance
    total_mileage_since_last_maintenance = row['Mileage (km)'] - (row['Mileage (km)'] // MAINTENANCE_INTERVAL_KM) * MAINTENANCE_INTERVAL_KM
    
    # Estimate time until next maintenance based on mileage and time
    km_until_next_maintenance = MAINTENANCE_INTERVAL_KM - mileage_since_last_maintenance
    days_until_next_maintenance = MAINTENANCE_INTERVAL_DAYS - days_since_last_maintenance

    # Debug print statements to track values
    print(f"Bus ID: {row['Bus_ID']}")
    print(f"Last Maintenance Date: {last_maintenance_date.date()}")
    print(f"Days Since Last Maintenance: {days_since_last_maintenance}")
    print(f"Total Mileage Since Last Maintenance: {total_mileage_since_last_maintenance}")
    print(f"Breakdowns Last Year: {row['Breakdowns (last year)']}")
    print(f"Downtime (days): {row['Downtime (days)']}")
    print(f"Driver Behavior Score: {row['Driver Behavior Score (out of 100)']}")
    print(f"KM until next maintenance: {km_until_next_maintenance}")
    print(f"Days until next maintenance: {days_until_next_maintenance}")
    print(f"Departure Location: {row['Departure']}")
    print(f"Destination Location: {row['Destination']}")
    print("------------------------------------------------")

    # Initialize the due status and date
    maintenance_status = "On Schedule"
    next_maintenance_date = last_maintenance_date + timedelta(days=MAINTENANCE_INTERVAL_DAYS)

    # Check if the bus needs maintenance
    if (days_since_last_maintenance >= MAINTENANCE_INTERVAL_DAYS or 
        total_mileage_since_last_maintenance >= MAINTENANCE_INTERVAL_KM or
        row['Breakdowns (last year)'] > BREAKDOWN_THRESHOLD or
        row['Downtime (days)'] > DOWNTIME_THRESHOLD or
        row['Driver Behavior Score (out of 100)'] < DRIVER_BEHAVIOR_THRESHOLD):
        
        maintenance_status = "Due Now"
        next_maintenance_date = datetime.now().date()  # Set to today if maintenance is due

    return maintenance_status, next_maintenance_date

# Apply the function to each bus in the dataset
df[['Maintenance Status', 'Next Maintenance Date']] = df.apply(calculate_maintenance_due, axis=1, result_type='expand')

# Convert the next maintenance date to datetime format
df['Next Maintenance Date'] = pd.to_datetime(df['Next Maintenance Date'])

# Format the next maintenance date as a string in 'YYYY-MM-DD'
df['Next Maintenance Date'] = df['Next Maintenance Date'].dt.strftime('%Y-%m-%d')

# Save the updated DataFrame to a .pkl file
df.to_pickle('maintenance/bus_maintenance_data.pkl')

print("Data processing complete and saved to bus_maintenance_data.pkl.")
