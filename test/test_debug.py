import pandas as pd

optimal = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')
fac_ids = optimal['facilities_opened_ids'].iloc[0]
print(f'facilities_opened_ids: {repr(fac_ids)}')
optimal_facilities = fac_ids.split(',')
optimal_facilities = [fid.strip() for fid in optimal_facilities]
print(f'Parsed list: {optimal_facilities}')
print(f'Test match FC04: {("FC04" in optimal_facilities)}')
print(f'Test match FC05: {("FC05" in optimal_facilities)}')

# Also test loading facility_map_data
facilities = pd.read_csv('data/candidate_facilities.csv')
print(f'\nFacility IDs in candidate_facilities.csv:')
print(facilities['Facility_ID'].tolist())

