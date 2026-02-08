import pandas as pd 
import numpy as np

print("Loading all data for Gurobi Optimization")

#Load base data files

#Stores with supply of devices to be refurbished
stores_df = pd.read_csv('data/stores_complete.csv')
print(f" Loaded {len(stores_df)} stores")

#Candidate Facilities
facilities_df = pd.read_csv('data/candidate_facilities.csv')
print(f" Loaded {len(facilities_df)} candidate facilities")

#Cost parameters
params_df = pd.read_csv('data/cost_parameters.csv')
print(f" Loaded cost parameters")

#ArcGIS solution (for comparison)
arcgis_stores_df = pd.read_csv('outputs/arc_gis_solution_stores.csv')
arcgis_facilities_df = pd.read_csv('outputs/arc_gis_solution_facilities.csv')
print(f" Loaded ArcGIS solution data")

#Creating data structures for optimization model

#Store list and supply dictionary
stores = stores_df['Store_ID'].tolist()
supply = dict(zip(stores_df['Store_ID'], stores_df['Annual_Returns']))

print(f'\n Stores Data:')
print(f" Number of Stores: {len(stores)}")
print(f" Total Supply of Devices for refurbishment: {sum(supply.values()):,} units/year ")

#Facility list and data dictionaries
facilities = facilities_df["Facility_ID"].tolist()
fixed_cost = dict(zip(facilities_df["Facility_ID"], facilities_df["Annual_Fixed_Cost"]))
capacity = dict(zip(facilities_df["Facility_ID"], facilities_df["Capacity_Units_Annual"]))

print (f" \n Facility data:")
print(f" Number of Candidate Facilities: {len(facilities)}")
print(f" Total Capacity of Candidate Facilities: {sum(capacity.values()):,} units/year ")
print(f" Fixed Cost Range: ${min(fixed_cost.values()):,} - ${max(fixed_cost.values()):,} per year")

# Calcuating Distance Matrix
print("\n Calculating Distances")

#Using Haversine formula to calculate great circle distance between stores and facilities co-ordinates

def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 3958.8 # Earth radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c 

    return distance

# Building distance dictionary
distance = {}
for _, store in stores_df.iterrows():
    for _, facility in facilities_df.iterrows():
        store_id = store["Store_ID"]
        facility_id = facility["Facility_ID"]

        dist = haversine_distance(
            store["Lat"], store["Lon"], facility["Latitude"], facility["Longitude"]
        )

        # Adding routing factor (road distance ~1.3 times straight line)
        dist_adjusted = dist * 1.3 

        distance[(store_id, facility_id)] = round(dist_adjusted,2)

print(f" Calculated {len(distance)} distance pairs")

#Show sample distances
print(f" \n Sample Distances (miles):")
sample_store = stores[0]
print(f" From {sample_store}: ")
for fac in facilities:
    print(f" to {fac}: {distance[(sample_store, fac)]:>6.1f} miles")

#Cost parametes

#REALISTIC TRANSPORT COST CALCULATION
unit_weight_lbs = params_df['unit_weight_lbs'].iloc[0]
freight_rate_per_cwt_per_100mi = params_df['freight_rate_per_cwt_per_100mi'].iloc[0]
pickup_dropoff_fee = params_df['pickup_dropoff_fee_per_stop'].iloc[0]
unload_handling_per_unit = params_df['unload_handling_per_unit'].iloc[0]
fuel_surcharge_pct = params_df['fuel_surcharge_pct'].iloc[0]

# Calculate REALISTIC transport cost per mile per unit:
# LTL freight rate from CA industry data: $3.50 per cwt per 100 miles
# Weight: 0.44 lbs = 0.0044 cwt
# Freight per unit per 100 miles = 0.0044 cwt × $3.50/cwt = $0.0154
# Freight per unit per MILE = $0.0154 / 100 miles = $0.000154/mile
# Plus fuel surcharge: $0.000154 × 1.12 = $0.000172/mile
# Plus handling at origin and destination = $0.35/unit (one-time, not per mile!)

# For optimization model, we'll model the variable cost per mile and fixed handling cost separately
weight_cwt = unit_weight_lbs / 100
freight_cost_per_mile = (weight_cwt * freight_rate_per_cwt_per_100mi) / 100
freight_cost_with_surcharge = freight_cost_per_mile * (1 + fuel_surcharge_pct)
transport_cost_per_mile = freight_cost_with_surcharge  # Variable cost per mile
handling_cost_per_unit= unload_handling_per_unit  # Fixed per unit, applied in objective

print(f"\n REALISTIC TRANSPORT COST BREAKDOWN:")
print(f" Unit Weight: {unit_weight_lbs} lbs = {weight_cwt*100:.4f} cwt")
print(f" Freight Rate (industry): ${freight_rate_per_cwt_per_100mi}/cwt per 100 miles")
print(f" Freight cost per unit per 100 miles: ${weight_cwt * freight_rate_per_cwt_per_100mi:.4f}")
print(f" Freight cost per unit per MILE: ${freight_cost_per_mile:.6f}")
print(f" Fuel surcharge ({fuel_surcharge_pct*100:.0f}%): ${freight_cost_with_surcharge:.6f}/mile")
print(f" Handling/Unloading per unit: ${unload_handling_per_unit:.2f} (fixed)")
print(f" TOTAL Transport Cost per mile per unit: ${transport_cost_per_mile:.6f}")
print(f" (Plus ${pickup_dropoff_fee:.0f} fixed pickup/drop-off per facility)")
print(f" Fixed Cost: ${min(fixed_cost.values()):,} - ${max(fixed_cost.values()):,}")

#Saving all data as pickle for easy loading

'''
Why use pickle?

1) Speed: Loading a pickled file is much faster than re-reading CSVs and recalculating everything
2) Preservation: Keeps your data structures exactly as they are (dictionaries, lists, calculations)
3) Convenience: Single file instead of multiple CSVs
'''

import pickle
data_package = {
    'stores': stores,
    'facilities': facilities,
    'supply': supply,
    'distance': distance,
    'fixed_cost': fixed_cost,
    'capacity': capacity,
    'transport_cost_per_mile': transport_cost_per_mile,
    'handling_cost_per_unit': handling_cost_per_unit,
    'pickup_dropoff_fee': pickup_dropoff_fee,
    'stores_df': stores_df,
    'facilities_df': facilities_df,
    'params_df': params_df,
    'arcgis_facilities_df': arcgis_facilities_df,
    'arcgis_stores_df': arcgis_stores_df
}

with open('data/gurobi_data_package.pkl', 'wb') as f:
    pickle.dump(data_package, f)

print(f"\n Saved complete data package")

#CREATING DISTANCE MATRIX CSV 

#Create distance matrix DataFrame
dist_matrix = pd.DataFrame(index=stores, columns = facilities)
for store in stores:
    for facility in facilities:
        dist_matrix.loc[store, facility] = distance[(store, facility)]

dist_matrix.to_csv('data/distance_matrix.csv')
print(f" Saved distance matrix as CSV")

#Summary Statistics
print(f" \n Data Summary for Gurobi Optimization:")
print(f" \n Decision Space:")
print(f" Binary facility variables: {len(facilities)}")
print(f" Binary assignment variables: {len(stores) * len(facilities)}")
print(f" Total binary variables: {len(facilities) + len(stores)*len(facilities)}")
print(f" Constraints: ~{len(stores) * 2 + len(facilities)}")

print(f" \n Problem Characteristics:")
total_supply = sum(supply.values())
total_capacity = sum(capacity.values())
print(f" Total Supply of devices to be refurbished: {total_supply:,} units/year")
print(f" Total Capacity of candidate facilities: {total_capacity:,} units/year")
print(f" Capacity/Supply Ratio: {total_capacity/total_supply:.2f}x")

avg_dist = np.mean(list(distance.values()))
min_dist = min(distance.values())
max_dist = max(distance.values())

print(f'\n Distance Statistics:')
print(f" Average Distance: {avg_dist:.2f} miles")
print(f" Minimum Distance: {min_dist:.2f} miles")
print(f" Maximum Distance: {max_dist:.2f} miles")