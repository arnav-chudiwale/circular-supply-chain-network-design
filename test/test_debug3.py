import pandas as pd 

print("Step 1: Load optimal solution")
optimal = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')

print("Step 2: Load facilities and stats")
facilities = pd.read_csv('data/candidate_facilities.csv')
facility_stats = pd.read_csv('outputs/gurobi_cost_facility_stats.csv', index_col=0)

print("Step 3: Merge") 
map_data = facilities.merge(
    facility_stats,
    left_on='Facility_ID',
    right_index=True,
    how='left'
)

print("Step 4: Add status")
optimal_facilities = optimal['facilities_opened_ids'].iloc[0].split(',')
optimal_facilities = [fid.strip() for fid in optimal_facilities]
print(f"Optimal facilities: {optimal_facilities}")

map_data["Status"] = map_data["Facility_ID"].apply(
    lambda x: "Selected" if x in optimal_facilities else "Not Selected"
)

print("Step 5: Select and format columns")
map_data = map_data[[
    'Facility_ID', 'Name', 'City', "Latitude", "Longitude", "Status", 
    'Capacity_Units_Annual', "Annual_Fixed_Cost", 'Num_Stores', "Total_Supply",
    "Utilization_Pct", "Avg_Distance"
]].copy()

map_data['Num_Stores'] = map_data['Num_Stores'].fillna(0).astype(int)
map_data['Total_Supply'] = map_data['Total_Supply'].fillna(0).astype(int) 
map_data['Utilization_Pct'] = map_data['Utilization_Pct'].fillna(0)
map_data['Avg_Distance'] = map_data['Avg_Distance'].fillna(0)

print("\nFinal map_data:")
print(map_data)

map_data.to_csv('data/powerbi/facility_map_data.csv', index = False)
print("\nSaved to data/powerbi/facility_map_data.csv")
