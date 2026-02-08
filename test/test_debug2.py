import pandas as pd 

optimal = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')
print(f"Columns in optimal: {optimal.columns.tolist()}")
print(f"First row of optimal:\n{optimal.iloc[0]}")

fac_ids = optimal['facilities_opened_ids'].iloc[0]
print(f"\nfacilities_opened_ids value: {repr(fac_ids)}")
optimal_facilities = fac_ids.split(',')
optimal_facilities = [fid.strip() for fid in optimal_facilities]
print(f"Parsed optimal_facilities list: {optimal_facilities}")

facilities = pd.read_csv('data/candidate_facilities.csv')
print(f"\nCandidate facilities Facility_IDs: {facilities['Facility_ID'].tolist()}")

# Now test the apply logic
print("\nTesting apply logic:")
for idx, row in facilities.iterrows():
    fid = row['Facility_ID']
    status = "Selected" if fid in optimal_facilities else "Not Selected"
    print(f"{fid}: {status}")
