import pandas as pd
import numpy as np

print("Analysing ARCGIS NETWORK ANALYST RESULTS")

#Read results
facilities = pd.read_csv('outputs/arc_gis_solution_facilities.csv')
stores = pd.read_csv('outputs/arc_gis_solution_stores.csv')

# Add Facility_ID based on index + 1 to match FacilityID in stores
facilities['Facility_ID'] = facilities.index + 1

#Filter to CHOSEN Facilities (FacilityType == 3)

chosen = facilities[facilities['FacilityType'] == 3].copy()

print(f" \n Facility Chosen:")
print(chosen[['Facility_ID', "Name", 'Capacity']])

print(f" \n Store Assignment Summary:")
for _, facility in chosen.iterrows():
    fac_id = facility["Facility_ID"]
    assigned_stores = stores[stores['FacilityID'] == fac_id]

    total_supply = assigned_stores['Weight'].sum()
    num_stores = len(assigned_stores)
    avg_distance = assigned_stores['DistanceToNetworkInMeters'].mean()


    print(f"\n {facility['Name']}:")
    print(f" Stores assigned: {num_stores}")
    print(f" Total supply volume assigned: {total_supply:,} units/year")
    print(f" Average distance to of store to chosen facility (miles): {avg_distance:.1f}")

total_distance = (stores['Weight'] * stores['DistanceToNetworkInMeters']).sum() # weighted distance
total_supply = stores['Weight'].sum()
average_weighted_distance = total_distance / total_supply

print(f" Total Supply from all stores: {total_supply:,} units/year")
print(f" Average weighted distance to chosen facilities (miles): {average_weighted_distance:.1f} miles")
print(f" Total weighted distance (supply volume * distance): {total_distance:,.0f} mile-units/year")

summary = pd.DataFrame([{
    'num_facilities': len(chosen),
    'total_supply': int(total_supply),
    'total_weighted_distance_miles': round(total_distance,2),
    'avg_weighted_distance_miles': round(average_weighted_distance,2),
    'solution_method': "ArcGIS Network Analyst - Minimize Impedance"
}])

summary.to_csv('outputs/arcgis_solution_summary.csv', index=False)
print("\n Summary of ARCGIS solution saved")