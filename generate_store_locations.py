import pandas as pd
import numpy as np 

np.random.seed(42)

#California major cities with approximate coordinates
# Format: (City, Latitude, Longitude, Number of stores)

california_cities = [
    ('San Francisco', 37.7749, -122.4194, 12),
    ('Los Angeles', 34.0522, -118.2437, 18),
    ('San Diego', 32.7157, -117.1611, 8),
    ('Sacramento', 38.5816, -121.4944, 4),
    ('San Jose', 37.3382, -121.8863, 6),
    ('Fresno', 36.7378, -119.7871, 3),
    ('Oakland', 37.8044, -122.2711, 4),
    ('Santa Barbara', 34.4208, -119.6982, 2),
    ('Riverside', 33.9806, -117.3755, 3)
    
]

stores_data = []
store_id = 1

print("Generating store locations")

for city, base_lat, base_long, num_stores in california_cities:
    for i in range(num_stores):
        # Adding random offset to cluster stores within the metro area 
        #  +- 15 degrees = +- 10 miles readius

        lat_offset = np.random.uniform(-0.15, 0.15)
        long_offset = np.random.uniform(-0.15, 0.15)

        # Randomly determining store type (flagship/standard)

        store_type = np.random.choice(
            ["Flagship", "Standard", "Standard", "Standard"]
        )

        stores_data.append({
            "Store_ID": f"ST{store_id:03d}",
            "City": city,
            "Latitude": round(base_lat + lat_offset, 6),
            "Longitude": round(base_long + long_offset, 6),
            "Store_Type": store_type
        })

        store_id += 1

    
#Creating Dataframe
stores_df = pd.DataFrame(stores_data)

print(f"\n Generated {len(stores_df)} stores")
print(f" Flagship stores: {(stores_df['Store_Type'] == 'Flagship').sum()} ")
print(f" Standard stores: {(stores_df['Store_Type'] == 'Standard').sum()} ")

print("\n First 10 stores: ")
print(stores_df.head(10).to_string(index=False))

#Save to CSV 
stores_df.to_csv('data/stores_locations.csv', index = False)
print("\n Store locations saved to 'data/stores_locations.csv'")
