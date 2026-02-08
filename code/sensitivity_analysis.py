import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from itertools import product

print("="*70)
print("SENSITIVITY ANALYSIS")
print("Testing impact of key parameters on NPV and optimal solution")
print("="*70)

# =============================================================================
# LOAD BASE DATA
# =============================================================================

with open('data/gurobi_data_package.pkl', 'rb') as f:
    data = pickle.load(f)

stores_df = data['stores_df']
params_df = data['params_df']
baseline = pd.read_csv('data/current_state_baseline.csv')
optimal = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')  # Updated to use optimal p solution
optimal_results = pd.read_csv('outputs/gurobi_optimal_p_results.csv')  # For detailed facility info
financial = pd.read_csv('outputs/financial_summary.csv')

base_npv = financial['NPV_3Year'].iloc[0]
base_capex = financial['Total_Capex'].iloc[0]

# Base values - calculate early so they're available for display
total_returns = stores_df['Annual_Returns'].sum()
grade_a_units = stores_df['Grade_A_Units'].sum()
grade_b_units = stores_df['Grade_B_Units'].sum()
grade_c_units = stores_df['Grade_C_Units'].sum()

grade_a_price_base = params_df['grade_a_resale_price'].iloc[0]
grade_b_price_base = params_df['grade_b_resale_price'].iloc[0]
grade_c_price_base = params_df['grade_c_parts_value'].iloc[0]

grade_a_handling = params_df['grade_a_handling_cost'].iloc[0]
grade_b_refurb = params_df['grade_b_refurb_cost'].iloc[0]
grade_c_processing = params_df['grade_c_processing_cost'].iloc[0]

facility_cost_base = optimal['total_fixed_cost'].iloc[0]
freight_cost_base = optimal['total_transport_cost'].iloc[0]  # Distance-based freight
handling_cost_base = optimal['total_handling_cost'].iloc[0]  # Per-unit handling
pickup_dropoff_base = optimal['total_pickup_dropoff_fee'].iloc[0]  # Fixed facility fee
logistics_cost_base = freight_cost_base + handling_cost_base + pickup_dropoff_base
facilities_info = optimal['facilities_opened'].iloc[0]  # Facility names and cities

print(f"\nBase case NPV: ${base_npv:,.0f}")
print(f"\nOptimal Solution Details:")
print(f" Facilities: {facilities_info}")
print(f" Annual Fixed Costs: ${facility_cost_base:,.0f}")
print(f" Annual Logistics Costs: ${logistics_cost_base:,.2f}")
print(f"   - Freight (distance-based): ${freight_cost_base:,.2f}")
print(f"   - Handling (per-unit): ${handling_cost_base:,.2f}")
print(f"   - Pickup/Drop-off (per facility): ${pickup_dropoff_base:,.2f}")

# =============================================================================
# DEFINE SENSITIVITY PARAMETERS
# =============================================================================

# Parameters to test
sensitivity_params = {
    'Resale Prices': {
        'base': 1.0,
        'range': [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20],
        'label': 'Resale Price Factor',
        'format': '{:.0%}'
    },
    'Fixed Costs': {
        'base': 1.0,
        'range': [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20],
        'label': 'Fixed Cost Factor',
        'format': '{:.0%}'
    },
    'Freight Cost': {
        'base': 1.0,
        'range': [0.50, 0.70, 0.85, 1.00, 1.15, 1.30, 1.50],
        'label': 'Freight Cost Factor',
        'format': '{:.0%}'
    },
    'Handling Cost': {
        'base': 1.0,
        'range': [0.50, 0.70, 0.85, 1.00, 1.15, 1.30, 1.50],
        'label': 'Handling Cost Factor',
        'format': '{:.0%}'
    },
    'Return Volume': {
        'base': 1.0,
        'range': [0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30],
        'label': 'Volume Factor',
        'format': '{:.0%}'
    },
    'CapEx': {
        'base': 1.0,
        'range': [0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30],
        'label': 'CapEx Factor',
        'format': '{:.0%}'
    }
}

print(f"\nTesting {len(sensitivity_params)} parameters:")
for param in sensitivity_params:
    print(f"  - {param}")

# =============================================================================
# ONE-WAY SENSITIVITY ANALYSIS
# =============================================================================

print("\n" + "="*70)
print("ONE-WAY SENSITIVITY ANALYSIS")
print("="*70)


discount_rate = 0.10
years = 3

sensitivity_results = {}

# Test each parameter
for param_name, param_config in sensitivity_params.items():
    print(f"\nTesting {param_name}...")
    
    param_results = []
    
    for value in param_config['range']:
        # Calculate NPV with this parameter value
        
        if param_name == 'Resale Prices':
            # Adjust resale prices
            revenue = (grade_a_units * grade_a_price_base * value +
                      grade_b_units * grade_b_price_base * value +
                      grade_c_units * grade_c_price_base * value)
            processing = (grade_a_units * grade_a_handling +
                         grade_b_units * grade_b_refurb +
                         grade_c_units * grade_c_processing)
            opex = facility_cost_base + freight_cost_base + handling_cost_base + pickup_dropoff_base + processing
            capex = base_capex
            
        elif param_name == 'Fixed Costs':
            revenue = (grade_a_units * grade_a_price_base +
                      grade_b_units * grade_b_price_base +
                      grade_c_units * grade_c_price_base)
            processing = (grade_a_units * grade_a_handling +
                         grade_b_units * grade_b_refurb +
                         grade_c_units * grade_c_processing)
            opex = facility_cost_base * value + freight_cost_base + handling_cost_base + pickup_dropoff_base + processing
            capex = base_capex
            
        elif param_name == 'Freight Cost':
            revenue = (grade_a_units * grade_a_price_base +
                      grade_b_units * grade_b_price_base +
                      grade_c_units * grade_c_price_base)
            processing = (grade_a_units * grade_a_handling +
                         grade_b_units * grade_b_refurb +
                         grade_c_units * grade_c_processing)
            # Adjust freight cost (distance-based component)
            freight_adjusted = freight_cost_base * value
            opex = facility_cost_base + freight_adjusted + handling_cost_base + pickup_dropoff_base + processing
            capex = base_capex
            
        elif param_name == 'Handling Cost':
            revenue = (grade_a_units * grade_a_price_base +
                      grade_b_units * grade_b_price_base +
                      grade_c_units * grade_c_price_base)
            processing = (grade_a_units * grade_a_handling +
                         grade_b_units * grade_b_refurb +
                         grade_c_units * grade_c_processing)
            # Adjust handling cost (per-unit component)
            handling_adjusted = handling_cost_base * value
            opex = facility_cost_base + freight_cost_base + handling_adjusted + pickup_dropoff_base + processing
            capex = base_capex
            
        elif param_name == 'Return Volume':
            revenue = (grade_a_units * grade_a_price_base * value +
                      grade_b_units * grade_b_price_base * value +
                      grade_c_units * grade_c_price_base * value)
            processing = (grade_a_units * grade_a_handling * value +
                         grade_b_units * grade_b_refurb * value +
                         grade_c_units * grade_c_processing * value)
            # Handling scales with volume; freight and pickup/drop-off are semi-fixed
            handling_scaled = handling_cost_base * value
            opex = facility_cost_base + freight_cost_base + handling_scaled + pickup_dropoff_base + processing
            capex = base_capex
            
        elif param_name == 'CapEx':
            revenue = (grade_a_units * grade_a_price_base +
                      grade_b_units * grade_b_price_base +
                      grade_c_units * grade_c_price_base)
            processing = (grade_a_units * grade_a_handling +
                         grade_b_units * grade_b_refurb +
                         grade_c_units * grade_c_processing)
            opex = facility_cost_base + freight_cost_base + handling_cost_base + pickup_dropoff_base + processing
            capex = base_capex * value
        
        # Calculate 3-year NPV
        npv = -capex
        for year in range(1, years + 1):
            annual_cf = revenue - opex
            pv = annual_cf / ((1 + discount_rate) ** year)
            npv += pv
        
        param_results.append({
            'Parameter_Value': value,
            'NPV': npv,
            'NPV_Change': npv - base_npv,
            'NPV_Change_Pct': ((npv - base_npv) / abs(base_npv)) * 100 if base_npv != 0 else 0
        })
    
    sensitivity_results[param_name] = pd.DataFrame(param_results)
    
    print(f"  NPV range: ${sensitivity_results[param_name]['NPV'].min():,.0f} to ${sensitivity_results[param_name]['NPV'].max():,.0f}")

# =============================================================================
# VISUALIZATION: TORNADO DIAGRAM
# =============================================================================

print("\n" + "="*70)
print("CREATING SENSITIVITY VISUALIZATIONS...")
print("="*70)

# Create tornado diagram (shows parameter impact)
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('Sensitivity Analysis: Impact on 3-Year NPV', fontsize=16, fontweight='bold')

axes_flat = axes.flatten()

for idx, (param_name, results_df) in enumerate(sensitivity_results.items()):
    ax = axes_flat[idx]
    
    param_config = sensitivity_params[param_name]
    
    # Plot
    x_values = results_df['Parameter_Value'].values
    y_values = results_df['NPV'].values / 1e6  # Convert to millions
    
    ax.plot(x_values, y_values, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    
    # Mark base case
    base_value = param_config['base']
    base_idx = results_df['Parameter_Value'].sub(base_value).abs().idxmin()
    base_npv = results_df.loc[base_idx, 'NPV'] / 1e6
    ax.plot(base_value, base_npv, 'ro', markersize=12, label='Base Case')
    
    # Zero line
    ax.axhline(0, color='red', linestyle='--', alpha=0.3)
    
    # Labels
    ax.set_xlabel(param_config['label'], fontsize=10, fontweight='bold')
    ax.set_ylabel('NPV ($M)', fontsize=10, fontweight='bold')
    ax.set_title(param_name, fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

# Remove extra subplot
if len(sensitivity_results) < len(axes_flat):
    fig.delaxes(axes_flat[-1])

plt.tight_layout()
plt.savefig('outputs/sensitivity_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: outputs/sensitivity_analysis.png")

# =============================================================================
# SPIDER CHART (Alternative Visualization)
# =============================================================================

fig, ax = plt.subplots(figsize=(12, 8))

for param_name, results_df in sensitivity_results.items():
    # Normalize: % change from base
    pct_changes = results_df['NPV_Change_Pct'].values
    param_values = results_df['Parameter_Value'].values
    
    # Convert parameter values to % change from base
    base_value = sensitivity_params[param_name]['base']
    param_pct_change = [(v - base_value) / base_value * 100 for v in param_values]
    
    ax.plot(param_pct_change, pct_changes, 'o-', linewidth=2, label=param_name, markersize=6)

ax.axhline(0, color='black', linestyle='-', alpha=0.3)
ax.axvline(0, color='black', linestyle='-', alpha=0.3)
ax.set_xlabel('Parameter Change from Base (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('NPV Change from Base (%)', fontsize=12, fontweight='bold')
ax.set_title('Spider Chart: Sensitivity of NPV to Key Parameters', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='best')

plt.tight_layout()
plt.savefig('outputs/sensitivity_spider_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: outputs/sensitivity_spider_chart.png")

# =============================================================================
# CALCULATE ELASTICITIES
# =============================================================================

print("\n" + "="*70)
print("PARAMETER ELASTICITIES")
print("(% change in NPV per 1% change in parameter)")
print("="*70)

elasticities = {}

for param_name, results_df in sensitivity_results.items():
    base_value = sensitivity_params[param_name]['base']
    
    # Find base case
    base_idx = results_df['Parameter_Value'].sub(base_value).abs().idxmin()
    
    # Find +10% and -10% cases
    high_value = base_value * 1.1
    low_value = base_value * 0.9
    
    high_idx = results_df['Parameter_Value'].sub(high_value).abs().idxmin()
    low_idx = results_df['Parameter_Value'].sub(low_value).abs().idxmin()
    
    npv_base = results_df.loc[base_idx, 'NPV']
    npv_high = results_df.loc[high_idx, 'NPV']
    npv_low = results_df.loc[low_idx, 'NPV']
    
    # Elasticity = (% change NPV) / (% change parameter)
    elasticity = ((npv_high - npv_low) / npv_base) / 0.2  # 20% parameter change
    
    elasticities[param_name] = elasticity
    
    print(f"\n{param_name}:")
    print(f"  Elasticity: {elasticity:.2f}")
    if abs(elasticity) > 1:
        print(f"  → HIGHLY SENSITIVE (elastic)")
    elif abs(elasticity) > 0.5:
        print(f"  → MODERATELY SENSITIVE")
    else:
        print(f"  → LOW SENSITIVITY (inelastic)")

# =============================================================================
# SAVE RESULTS
# =============================================================================

# Save all sensitivity results
for param_name, results_df in sensitivity_results.items():
    filename = f"outputs/sensitivity_{param_name.lower().replace(' ', '_')}.csv"
    results_df.to_csv(filename, index=False)
    print(f"✓ Saved: {filename}")

# Save elasticities
elasticity_df = pd.DataFrame([elasticities])
elasticity_df.to_csv('outputs/sensitivity_elasticities.csv', index=False)
print("✓ Saved: outputs/sensitivity_elasticities.csv")

print("\n" + "="*70)
print("✅ SENSITIVITY ANALYSIS COMPLETE")
print("="*70)
print("\nKey findings:")
print("  Most sensitive parameters:")
sorted_elasticities = sorted(elasticities.items(), key=lambda x: abs(x[1]), reverse=True)
for param, elast in sorted_elasticities[:3]:
    print(f"    - {param}: {elast:.2f}")