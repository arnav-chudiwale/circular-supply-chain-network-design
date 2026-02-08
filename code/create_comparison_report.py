import pandas as pd
import numpy as np
from datetime import datetime
import re

print("="*70)
print("CREATING MASTER COMPARISON REPORT")
print("="*70)

# =============================================================================
# LOAD ALL RESULTS
# =============================================================================

# Current state
baseline = pd.read_csv('data/current_state_baseline.csv')

# Optimization results
distance_model = pd.read_csv('outputs/gurobi_distance_minimization_summary.csv')
cost_model = pd.read_csv('outputs/gurobi_cost_summary.csv')
optimal_model = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')

# Financial
financial = pd.read_csv('outputs/financial_summary.csv')

# Load facility reference data
facilities_ref = pd.read_csv('data/candidate_facilities.csv')

# ArcGIS (if available)
try:
    arcgis_summary = pd.read_csv('outputs/arcgis_solution_summary.csv')
    has_arcgis = True
except:
    has_arcgis = False

print("\n✓ Loaded all result files")

# =============================================================================
# HELPER FUNCTION TO STANDARDIZE FACILITY NAMES
# =============================================================================

def format_facilities_standardized(facility_input, facilities_df):
    """
    Standardize facility names to format: facility_id (City, State(abr))
    Handles various input formats: facility IDs, names, or mixed formats
    """
    if facility_input is None or facility_input == 'None' or facility_input == '':
        return None
    
    # Create mapping dictionaries
    id_to_info = {}
    name_to_id = {}
    
    for _, row in facilities_df.iterrows():
        fid = row['Facility_ID']
        city = row['City']
        name = row['Name']
        
        # Determine state based on city
        state_map = {
            'Fremont': 'CA',
            'Ontario': 'CA',
            'San Diego': 'CA',
            'Fresno': 'CA',
            'Reno': 'NV'
        }
        state = state_map.get(city, 'CA')
        
        id_to_info[fid] = f"{fid} ({city}, {state})"
        name_to_id[name] = fid
    
    facility_input = str(facility_input).strip()
    
    # If it's a single facility name (like "Los Angeles Metro")
    if facility_input in name_to_id:
        fid = name_to_id[facility_input]
        return id_to_info[fid]
    
    # If it's already in a complex format, parse and reformat
    if '(' in facility_input:
        # Extract facility IDs from format like "FC04 (Central Valley, Fresno), FC05 (...)"
        fids = re.findall(r'(FC\d+)', facility_input)
        return ', '.join([id_to_info.get(fid, fid) for fid in fids])
    
    # If it's a list of IDs separated by comma
    if ',' in facility_input:
        fids = [f.strip() for f in facility_input.split(',')]
        # Check if these are IDs or names
        formatted = []
        for f in fids:
            if f in id_to_info:
                formatted.append(id_to_info[f])
            elif f in name_to_id:
                formatted.append(id_to_info[name_to_id[f]])
            else:
                formatted.append(f)
        return ', '.join(formatted)
    
    # If it's a single facility ID
    if facility_input in id_to_info:
        return id_to_info[facility_input]
    
    return facility_input

# =============================================================================
# BUILD COMPARISON TABLE
# =============================================================================

comparison_data = []

# Current State
comparison_data.append({
    'Scenario': 'Current State (Bulk Recycling)',
    'Approach': 'As-Is',
    'Num_Facilities': 0,
    'Facilities_Opened': format_facilities_standardized(None, facilities_ref),
    'Annual_Recovery': baseline['annual_recovery'].iloc[0],
    'Annual_Fixed_Cost': 0,
    'Annual_Transport_Cost': 0,
    'Annual_Processing_Cost': 0,
    'Total_Annual_Cost': 0,
    'Net_Annual_Benefit': baseline['annual_recovery'].iloc[0],
    'Avg_Distance_Miles': 0,
    'Total_CapEx': 0,
    'NPV_3Year': 0,
    'Payback_Years': 0,
    'ROI_Percent': 0,
    'Notes': 'Baseline - bulk sale to recycler'
})

# ArcGIS Solution (if available)
if has_arcgis:
    # Extract the selected facility from ArcGIS results (facility with demand > 0)
    arcgis_facilities = pd.read_csv('outputs/arc_gis_solution_facilities.csv')
    selected_facility = arcgis_facilities[arcgis_facilities['DemandCount'] > 0]['Name'].iloc[0] if len(arcgis_facilities[arcgis_facilities['DemandCount'] > 0]) > 0 else 'Unknown'
    
    comparison_data.append({
        'Scenario': 'ArcGIS Network Analyst',
        'Approach': 'Minimize Distance',
        'Num_Facilities': arcgis_summary['num_facilities'].iloc[0],
        'Facilities_Opened': format_facilities_standardized(selected_facility, facilities_ref),
        'Annual_Recovery': np.nan,
        'Annual_Fixed_Cost': np.nan,
        'Annual_Transport_Cost': np.nan,
        'Annual_Processing_Cost': np.nan,
        'Total_Annual_Cost': np.nan,
        'Net_Annual_Benefit': np.nan,
        'Avg_Distance_Miles': arcgis_summary['avg_weighted_distance_miles'].iloc[0],
        'Total_CapEx': np.nan,
        'NPV_3Year': np.nan,
        'Payback_Years': np.nan,
        'ROI_Percent': np.nan,
        'Notes': 'Geographic optimization only'
    })

# Gurobi Distance Model
comparison_data.append({
    'Scenario': 'Gurobi: Distance Minimization',
    'Approach': 'Minimize Weighted Distance',
    'Num_Facilities': distance_model['num_facilities'].iloc[0],
    'Facilities_Opened': format_facilities_standardized(distance_model['facilities_opened'].iloc[0], facilities_ref),
    'Annual_Recovery': np.nan,
    'Annual_Fixed_Cost': np.nan,
    'Annual_Transport_Cost': np.nan,
    'Annual_Processing_Cost': np.nan,
    'Total_Annual_Cost': np.nan,
    'Net_Annual_Benefit': np.nan,
    'Avg_Distance_Miles': distance_model['average_weighted_distance'].iloc[0],
    'Total_CapEx': np.nan,
    'NPV_3Year': np.nan,
    'Payback_Years': np.nan,
    'ROI_Percent': np.nan,
    'Notes': 'Validates ArcGIS approach'
})

# Gurobi Cost Model
comparison_data.append({
    'Scenario': 'Gurobi: Cost Minimization (p=2)',
    'Approach': 'Minimize Total Cost',
    'Num_Facilities': cost_model['num_facilities'].iloc[0],
    'Facilities_Opened': format_facilities_standardized(cost_model['facilities_opened'].iloc[0], facilities_ref),
    'Annual_Recovery': np.nan,
    'Annual_Fixed_Cost': cost_model['total_fixed_cost'].iloc[0],
    'Annual_Transport_Cost': cost_model['total_transport_cost'].iloc[0],
    'Annual_Processing_Cost': np.nan,
    'Total_Annual_Cost': cost_model['total_annual_cost'].iloc[0],
    'Net_Annual_Benefit': np.nan,
    'Avg_Distance_Miles': cost_model['avg_weighted_distance'].iloc[0],
    'Total_CapEx': np.nan,
    'NPV_3Year': np.nan,
    'Payback_Years': np.nan,
    'ROI_Percent': np.nan,
    'Notes': 'Economic optimization'
})

# Gurobi Optimal p Model (RECOMMENDED)
comparison_data.append({
    'Scenario': 'RECOMMENDED: Optimal Facility Count',
    'Approach': 'Minimize Total Cost (optimal p)',
    'Num_Facilities': optimal_model['optimal_p'].iloc[0],
    'Facilities_Opened': format_facilities_standardized(optimal_model['facilities_opened'].iloc[0], facilities_ref),
    'Annual_Recovery': financial['Proposed_Annual_Recovery'].iloc[0],
    'Annual_Fixed_Cost': optimal_model['total_fixed_cost'].iloc[0],
    'Annual_Transport_Cost': optimal_model['total_transport_cost'].iloc[0],
    'Annual_Processing_Cost': np.nan,  # Embedded in recovery calc
    'Total_Annual_Cost': optimal_model['total_annual_cost'].iloc[0],
    'Net_Annual_Benefit': financial['Proposed_Annual_Recovery'].iloc[0],
    'Avg_Distance_Miles': optimal_model['avg_distance_miles'].iloc[0],
    'Total_CapEx': financial['Total_Capex'].iloc[0],
    'NPV_3Year': financial['NPV_3Year'].iloc[0],
    'Payback_Years': financial['Payback_Period_Years'].iloc[0],
    'ROI_Percent': financial['ROI_Percentage'].iloc[0],
    'Notes': 'Full economic + financial analysis'
})

comparison_df = pd.DataFrame(comparison_data)

# =============================================================================
# SAVE COMPARISON TABLE
# =============================================================================

comparison_df.to_csv('outputs/master_comparison_table.csv', index=False)
print("\n✓ Saved: outputs/master_comparison_table.csv")

# =============================================================================
# CREATE EXCEL WORKBOOK WITH FORMATTED COMPARISON
# =============================================================================

print("\nCreating formatted Excel workbook...")

with pd.ExcelWriter('outputs/optimization_results_comparison.xlsx', engine='openpyxl') as writer:
    # Sheet 1: Master Comparison
    comparison_df.to_excel(writer, sheet_name='Comparison', index=False)
    
    # Sheet 2: Financial Details
    financial.to_excel(writer, sheet_name='Financial Summary', index=False)
    
    # Sheet 3: Cash Flows
    cash_flows = pd.read_csv('outputs/financial_cash_flows.csv')
    cash_flows.to_excel(writer, sheet_name='Cash Flows', index=False)
    
    # Sheet 4: Sensitivity
    try:
        sensitivity_summary = []
        for param in ['Resale Prices', 'Fixed Costs', 'Transport Cost', 'Return Volume', 'CapEx']:
            df = pd.read_csv(f"outputs/sensitivity_{param.lower().replace(' ', '_')}.csv")
            sensitivity_summary.append({
                'Parameter': param,
                'Min_NPV': df['NPV'].min(),
                'Max_NPV': df['NPV'].max(),
                'Range': df['NPV'].max() - df['NPV'].min()
            })
        sensitivity_df = pd.DataFrame(sensitivity_summary)
        sensitivity_df.to_excel(writer, sheet_name='Sensitivity Summary', index=False)
    except:
        pass
    
    # Sheet 5: Optimal p Analysis
    try:
        optimal_p_comparison = pd.read_csv('outputs/gurobi_optimal_p_comparison.csv')
        optimal_p_comparison.to_excel(writer, sheet_name='Optimal p Analysis', index=False)
    except:
        pass

print("✓ Saved: outputs/optimization_results_comparison.xlsx")

# =============================================================================
# PRINT EXECUTIVE SUMMARY
# =============================================================================

print("\n" + "="*70)
print("EXECUTIVE SUMMARY")
print("="*70)

recommended = comparison_df[comparison_df['Scenario'].str.contains('RECOMMENDED')].iloc[0]
current = comparison_df[comparison_df['Scenario'].str.contains('Current')].iloc[0]

print(f"\nCURRENT STATE:")
print(f"  Annual recovery: ${current['Net_Annual_Benefit']:,.0f}")
print(f"  Operating model: Bulk recycling")
print(f"  Capital required: $0")

print(f"\nRECOMMENDED SOLUTION:")
print(f"  Facilities: {int(recommended['Num_Facilities'])}")
print(f"  Locations: {recommended['Facilities_Opened']}")
print(f"  Annual recovery: ${recommended['Net_Annual_Benefit']:,.0f}")
print(f"  Capital required: ${recommended['Total_CapEx']:,.0f}")

improvement = recommended['Net_Annual_Benefit'] - current['Net_Annual_Benefit']
improvement_pct = (improvement / current['Net_Annual_Benefit']) * 100

print(f"\nVALUE CREATION:")
print(f"  Incremental annual benefit: ${improvement:,.0f}")
print(f"  Improvement: {improvement_pct:.1f}%")
print(f"  3-year NPV: ${recommended['NPV_3Year']:,.0f}")
print(f"  Payback period: {recommended['Payback_Years']:.1f} years")
print(f"  ROI: {recommended['ROI_Percent']:.1f}%")

print("\n" + "="*70)
print("✅ COMPARISON REPORT COMPLETE")
print("="*70)