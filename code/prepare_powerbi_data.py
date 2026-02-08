import pandas as pd 
import os 
from datetime import datetime

print(f"\n Preaparing data for POWER BI")

#Create powerbi data folder
os.makedirs('data/powerbi', exist_ok = True)

# COllect all relevant data 

files_to_copy = {
    #Core data 
    'data/stores_complete.csv': 'data/powerbi/stores.csv',
    'data/candidate_facilities.csv': 'data/powerbi/facilities.csv',
    'data/cost_parameters.csv': 'data/powerbi/parameters.csv',
    'data/current_state_baseline.csv': 'data/powerbi/baseline.csv',

    #Optimization results
    'outputs/gurobi_optimal_p_summary.csv': 'data/powerbi/optimal_solution.csv',
    'outputs/gurobi_optimal_p_results.csv': 'data/powerbi/p_comparison.csv',
    'outputs/gurobi_cost_assignments.csv': 'data/powerbi/assignments.csv',
    'outputs/gurobi_cost_facility_stats.csv': 'data/powerbi/facility_stats.csv',

    #Financial Results
    'outputs/financial_summary.csv': 'data/powerbi/financial_summary.csv',
    'outputs/financial_cash_flows.csv': 'data/powerbi/cash_flows.csv',
    'outputs/financial_scenarios.csv': 'data/powerbi/scenarios.csv',

    #Comparison
    'outputs/master_comparison_table.csv': 'data/powerbi/comparison.csv'

}

print("\n Copying files to PowerBI data folder")
copied = 0 
for source, dest in files_to_copy.items():
    if os.path.exists(source):
        df = pd.read_csv(source)
        df.to_csv(dest, index=False)
        copied += 1 
        print(f" Copied: {source} -> {dest}")
    else:
        print(f" Warning: Source file not found - {source}")

print(f"\n Completed copying {copied}/{len(files_to_copy)} files to PowerBI data folder")

# Creating Supplementary tables for dashboarding

print("\n Creating Supplementary tables...")

# 1. KPI Summary Table (for card visuals)
optimal = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')
financial = pd.read_csv('outputs/financial_summary.csv')
baseline = pd.read_csv('data/current_state_baseline.csv')

kpi_data = {
    'KPI_Name': [
        'Optimal Facilities',
        "Current Recovery",
        "Proposed Recovery",
        "Incremental Value",
        'Improvement %',
        'Total Capex',
        'NPV (3 Year)',
        "Payback Period Years",
        "ROI (%)",
        "Avg Distance (miles)",
        "Facilities Opened"
    ],
    'Value': [
        int(optimal['optimal_p'].iloc[0]),
        baseline['annual_recovery'].iloc[0],
        financial["Proposed_Annual_Recovery"].iloc[0],
        financial["Incremental_Annual_Value"].iloc[0],
        financial["Improvement_Percentage"].iloc[0],
        financial['Total_Capex'].iloc[0],
        financial['NPV_3Year'].iloc[0],
        financial['Payback_Period_Years'].iloc[0],
        financial['ROI_Percentage'].iloc[0],
        optimal['avg_distance_miles'].iloc[0],
        optimal['facilities_opened'].iloc[0]
    ],
    'Display_Value': [
        f"{int(optimal['optimal_p'].iloc[0])} Facilities",
        f"${baseline['annual_recovery'].iloc[0]:,.0f}",
        f"${financial['Proposed_Annual_Recovery'].iloc[0]:,.0f}",
        f"${financial['Incremental_Annual_Value'].iloc[0]:,.0f}",
        f"{financial['Improvement_Percentage'].iloc[0]:.1f}%",
        f"${financial['Total_Capex'].iloc[0]:,.0f}",
        f"${financial['NPV_3Year'].iloc[0]:,.0f}",
        f"{financial['Payback_Period_Years'].iloc[0]:.1f} Years",
        f"{financial['ROI_Percentage'].iloc[0]:.1f}%",
        f"{optimal['avg_distance_miles'].iloc[0]:.1f} Miles",
        optimal['facilities_opened'].iloc[0]
    ],
    'Category': [
        'Network',
        'Financial',
        'Financial',
        'Financial',
        'Financial',
        'Financial',
        'Financial',
        'Financial',
        'Financial',
        'Network',
        'Network'
    ]
}

kpi_df = pd.DataFrame(kpi_data)
kpi_df.to_csv('data/powerbi/kpi_summary.csv', index = False)

# 2. Facility Location Data (for mapping visuals)
facilities = pd.read_csv('data/candidate_facilities.csv')
facility_stats = pd.read_csv('outputs/gurobi_cost_facility_stats.csv', index_col=0)

# merge to get chosen facilities 
map_data = facilities.merge(
    facility_stats,
    left_on='Facility_ID',
    right_index=True,
    how='left'
)

# Add status
optimal_facilities = optimal['facilities_opened'].iloc[0].split(', ')
map_data["Status"] = map_data["Facility_ID"].apply(
    lambda x: "Chosen" if x in optimal_facilities else "Not Selected"
)

#Select relevant columns for map 
map_data = map_data[[
    'Facility_ID', 'Name', 'City', "Latitude", "Longitude", "Status", 
    'Capacity_Units_Annual', "Annual_Fixed_Cost", 'Num_Stores', "Total_Supply",
    "Utilization_Pct", "Avg_Distance"
]].copy()

#FIll NaN for not selected facilities 
map_data['Num_Stores'] = map_data['Num_Stores'].fillna(0).astype(int)
map_data['Total_Supply'] = map_data['Total_Supply'].fillna(0).astype(int)
map_data['Utilization_Pct'] = map_data['Utilization_Pct'].fillna(0)
map_data['Avg_Distance'] = map_data['Avg_Distance'].fillna(0)

map_data.to_csv('data/powerbi/facility_map_data.csv', index = False)
print("\n facility_map_data.csv created with facility details and optimal solution status for mapping visuals")

# 3. Store Assignment Data (for detailed analysis)
stores = pd.read_csv('data/stores_complete.csv')
assignments = pd.read_csv('outputs/gurobi_cost_assignments.csv')

store_assignments = stores.merge(
    assignments,
    on = "Store_ID",
    how = "left"
)

store_assignments.to_csv('data/powerbi/store_assignments.csv', index = False)
print("\n store_assignments.csv created with store details and assigned facilities for detailed analysis")

#4. TIme series data for cash flow visuals
cash_flows = pd.read_csv('outputs/financial_cash_flows.csv')
cash_flows["Year_Label"] = 'Year' + cash_flows["Year"].astype(str)
cash_flows.to_csv('data/powerbi/financial_cash_flows_formatted.csv', index = False)
print("\n financial_cash_flows_formatted.csv created with formatted year labels for cash flow visuals")

# Creating data dictionary for PowerBI 
data_dictionary = """
POWER BI DATA DICTIONARY
========================

Files in data/powerbi/:

1. stores.csv - All Apple Store locations with demand
   - Store_ID, Store_Name, City, Lat, Lon
   - Annual_Returns, Grade_A/B/C_Units

2. facilities.csv - Candidate facility locations
   - Facility_ID, Name, City, Latitude, Longitude
   - Capacity_Units_Annual, Annual_Fixed_Cost

3. parameters.csv - Cost parameters
   - All pricing and cost assumptions

4. baseline.csv - Current state metrics
   - Current annual recovery value

5. optimal_solution.csv - Recommended solution
   - Optimal p, facilities opened, costs

6. p_comparison.csv - Sensitivity to facility count
   - Costs for p=1,2,3,4,5

7. assignments.csv - Store-to-facility assignments
   - Store_ID, Facility_ID, Distance, Transport_Cost

8. facility_stats.csv - Facility-level metrics
   - Stores served, utilization, costs by facility

9. financial_summary.csv - Financial overview
   - NPV, ROI, payback, incremental value

10. cash_flows.csv - 3-year projections
    - Year-by-year revenue, costs, NPV

11. scenarios.csv - Risk scenarios
    - Base, Conservative, Optimistic cases

12. comparison.csv - Solution comparison
    - Current vs ArcGIS vs Gurobi models

13. kpi_summary.csv - Key metrics for cards
    - Pre-formatted KPI values

14. facility_map_data.csv - Geographic visualization
    - Lat/Lon with chosen/not chosen status

15. store_assignments.csv - Full store details
    - Merged stores + assignments

16. cash_flows_formatted.csv - Formatted for charts
    - Year labels for better display

RELATIONSHIPS TO CREATE:
- facilities.Facility_ID → assignments.Facility_ID
- facilities.Facility_ID → facility_stats.Facility_ID (index)
- stores.Store_ID → assignments.Store_ID
"""

with open('data/powerbi/DATA_DICTIONARY.txt', 'w', encoding='utf-8') as f: 
    f.write(data_dictionary)

print("\n Data Dictionary created")
