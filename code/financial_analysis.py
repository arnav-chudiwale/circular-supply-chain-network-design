import pandas as pd
import numpy as np
import pickle 
from datetime import datetime 
import matplotlib.pyplot as plt 

print("\n FINANCIAL BUSINESS CASE ANALYSIS")
print("3-year NPV, ROI and Payback Period Calculations")

#Loading all data 

with open('data/gurobi_data_package.pkl', 'rb') as f: 
    data = pickle.load(f)

stores_df = data["stores_df"]
params_df = data["params_df"]

# Loading optimization results 
baseline = pd.read_csv('data/current_state_baseline.csv')
optimal_solution = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')

print("\n Loaded all Data sources")

#Current baseline 

print("\n CURRENT STATE - BULK RECYCLING MODEL")

total_returns = baseline['total_returns'].iloc[0]
bulk_payout = baseline['bulk_payout_per_unit'].iloc[0]
current_annual_recovery = baseline['annual_recovery'].iloc[0]

print(f"\n Total Annual Returns: {total_returns:,} units")
print(f" Bulk Payout per Unit: ${bulk_payout:.2f}")
print(f" Current Annual Recovery: ${current_annual_recovery:,.0f}")

print(f"\nCurrent State -")
print(f" - No sorting or grading")
print(f" - Bulk Sale to 3rd Party Recycler")
print(f" - Landfill Diversion Rate: ~ 35%")
print(f" - Processing Cycle Time: 60+ days")
print(f" - No Capital Investment required")

#Proposed State (Optimized Network)

print(f" Proposed State - OPTIMIZED REFURBISHMENT NETWORK")

#Get facility operating costs from optimal solution
num_facilities = int(optimal_solution['optimal_p'].iloc[0])
facilities_opened = optimal_solution['facilities_opened'].iloc[0]
facilities_opened_ids = optimal_solution['facilities_opened_ids'].iloc[0]
annual_facility_cost = optimal_solution['total_fixed_cost'].iloc[0]
annual_pickup_dropoff_cost = optimal_solution['total_pickup_dropoff_fee'].iloc[0]
annual_handling_cost = optimal_solution['total_handling_cost'].iloc[0]
annual_transport_cost = optimal_solution['total_transport_cost'].iloc[0]
total_annual_logistics_cost = annual_pickup_dropoff_cost + annual_handling_cost + annual_transport_cost

print(f"\n Network Configuration:")
print(f'Number of Facilities to Open: {num_facilities}')
print(f"\n Facility Details:")
print(f" {facilities_opened}")
print(f"\n Annual Fixed Costs: ${annual_facility_cost:,.0f}")
print(f"\n Annual Logistics Costs Breakdown:")
print(f" - Pickup/Drop-off Fees: ${annual_pickup_dropoff_cost:,.2f}")
print(f" - Handling/Unloading: ${annual_handling_cost:,.2f}")
print(f" - Freight (Distance-based): ${annual_transport_cost:,.2f}")
print(f" - TOTAL Logistics Costs: ${total_annual_logistics_cost:,.2f}")

#Calculate revenue by grade 
grade_a_units = stores_df['Grade_A_Units'].sum()
grade_b_units = stores_df['Grade_B_Units'].sum()
grade_c_units = stores_df['Grade_C_Units'].sum()

# Get pricing from parameters
grade_a_price = params_df['grade_a_resale_price'].iloc[0]
grade_b_price = params_df['grade_b_resale_price'].iloc[0]
grade_c_price = params_df['grade_c_parts_value'].iloc[0]

grade_a_handling = params_df['grade_a_handling_cost'].iloc[0]
grade_b_refurb = params_df['grade_b_refurb_cost'].iloc[0]
grade_c_processing = params_df['grade_c_processing_cost'].iloc[0]

# Gross revenue 
grade_a_revenue = grade_a_units * grade_a_price
grade_b_revenue = grade_b_units * grade_b_price
grade_c_revenue = grade_c_units * grade_c_price
total_gross_revenue = grade_a_revenue + grade_b_revenue + grade_c_revenue

#Processing costs 
grade_a_cost = grade_a_units * grade_a_handling
grade_b_cost = grade_b_units * grade_b_refurb
grade_c_cost = grade_c_units * grade_c_processing
total_processing_cost = grade_a_cost + grade_b_cost + grade_c_cost

#Net revenue before network costs 
net_revenue_before_logistics = total_gross_revenue - total_processing_cost

# Printing revenue by grade 
print(f"\n Revenue by Grade: ")
print(f" Grade A: (Like New) ({grade_a_units:,}) units * ${grade_a_price:.2f}: ${grade_a_revenue:,.0f}")
print(f" Grade B: (Refurbishable) ({grade_b_units:,}) units * ${grade_b_price:.2f}: ${grade_b_revenue:,.0f}")
print(f" Grade C: (Parts) ({grade_c_units:,}) units * ${grade_c_price:.2f}: ${grade_c_revenue:,.0f}")
print(f" Total Gross Revenue: ${total_gross_revenue:,.0f}")

print(f'\n Processing costs:')
print(f" Grade A Handling: ({grade_a_units:,}) units * ${grade_a_handling:.2f}: ${grade_a_cost:,.0f}")
print(f" Grade B Refurbishment: ({grade_b_units:,}) units * ${grade_b_refurb:.2f}: ${grade_b_cost:,.0f}")
print(f" Grade C Disassembly: ({grade_c_units:,}) units * ${grade_c_processing:.2f}: ${grade_c_cost:,.0f}")
print(f" Total Processing Costs: ${total_processing_cost:,.0f}")

# Total Operating Costs = Total Processing Costs + Network Costs (Facility + Transportation)
total_operating_cost = (annual_facility_cost + total_annual_logistics_cost + total_processing_cost)

# Net recovery 
proposed_net_recovery = total_gross_revenue - total_operating_cost

print(f" \n Proposed State Annual PnL: ")
print(f" Gross Revenue: ${total_gross_revenue:,.0f}")
print(f" Total Operating Costs (Processing + Facility + Logistics): ${total_operating_cost:,.0f}")
print(f" - Annual Facility Fixed Cost: ${annual_facility_cost:,.0f}")
print(f" - Annual Logistics Cost (Freight + Handling + Pickup/Drop-off): ${total_annual_logistics_cost:,.2f}")
print(f"   • Freight: ${annual_transport_cost:,.2f}")
print(f"   • Handling: ${annual_handling_cost:,.2f}")
print(f"   • Pickup/Drop-off: ${annual_pickup_dropoff_cost:,.2f}")
print(f" - Total Processing Costs: ${total_processing_cost:,.0f}")
print(f" Net Recovery: ${proposed_net_recovery:,.0f}")


'''
INCREMENTAL VALUE ANALYSIS
'''
incremental_annual_value = proposed_net_recovery - current_annual_recovery
improvement_pct = (incremental_annual_value / current_annual_recovery)

print(f" \n Current State Annual Recovery: ${current_annual_recovery:,.0f}")
print(f" Proposed State Annual Recovery: ${proposed_net_recovery:,.0f}")
print(f" Incremental Annual Value: ${incremental_annual_value:,.0f}")
print(f" Improvement Percentage: {improvement_pct:.2%}")

'''
Capital Investment Analysis 
'''
print(f"\n CAPITAL INVESTMENT ANALYSIS")

#Estimating one time setup costs 
#Industry Benchmarks for facility setup costs

capex_per_facility = {
    'facility_buildout': 500000,  #Lease Improvements and layout 
    'sorting_equipment': 150000, #Automated Sorting systems
    'testing_equipment': 100000, #Diagnostic and Testing stations 
    'refurb_equipment': 200000, #repair tools, parts inventory 
    'it_systems': 75000, #Inventory and Warehouse management systems
    'safety_compliance': 50000, #Safety and Compliance measures
    'initial_training': 50000 #Initial staff training and onboarding

}

capex_per_facility_total = sum(capex_per_facility.values())
total_capex = capex_per_facility_total * num_facilities

print(f" \n Capital Expenditure (CapEx) Breakdown per Facility:")
for item, cost in capex_per_facility.items():
    print(f" - {item.replace('_', ' ').title()}: ${cost:,.0f}")

print(f" Total CapEx per Facility: ${capex_per_facility_total:,.0f}")
print(f" Total CapEx for {num_facilities} Facilities: ${total_capex:,.0f}")

'''
3-Year Net Present Value(NPV) Analysis 
'''

#Parameters 
discount_rate = 0.10 # 10% WACC (Weighted Average Cost of Capital for financing)
years = 3

#Assumptions for projections
annual_growth_rate = 0.03 # 3% annual growth in returns volume
cost_inflation = 0.02 # 2% annual cost inflation 

print(f"\n Assumptions for 3-Year Projections:")
print(f" Discount Rate on Capital: {discount_rate*100}%")
print(f"Analysis Period: {years} years")
print(f" Volume growth rate year-over-year: {annual_growth_rate*100}%/year")
print(f" Cost inflation rate: {cost_inflation*100}%/year")

#Building Cash Flow Projections 
cash_flows = []

for year in range(years + 1 ): # Years = 0,1,2,3
    if year == 0:
        # Initial Capital Expenditure (CapEx)
        cf = {
            'Year': year,
            "Returns_Volume": total_returns,
            "Gross_Revenue": 0,
            "Operating_Costs": 0,
            "Capital_Expenditure": total_capex,
            "Net_Cash_Flow": -total_capex,
            'Discount_Factor': 1.0,
            "Present_Value": -total_capex
        }
    else: 
        #Operating years 
        volume = total_returns * ((1+ annual_growth_rate) ** (year))

        # Scale revenues with volume growth
        revenue = total_gross_revenue * ((1 + annual_growth_rate) ** (year))

        # Scale operating costs with volume and cost inflation
        opex = total_operating_cost * ((1 + annual_growth_rate) ** (year)) * ((1+ cost_inflation) ** (year))

        #Net cash flow for the year
        ncf = revenue - opex 

        # Present Value
        discount_factor = 1/((1 + discount_rate) ** year)
        pv = ncf * discount_factor

        cf = {
            "Year": year,
            'Returns_Volume': int(volume),
            "Gross_Revenue": revenue,
            "Operating_Costs": opex,
            "CapEx": 0,
            "Net_Cash_Flow": ncf,
            "Discount_Factor": discount_factor,
            "Present_Value": pv
        }

    cash_flows.append(cf)
cash_flow_df = pd.DataFrame(cash_flows)

# Calculate Net Present Value (NPV
npv = cash_flow_df["Present_Value"].sum()

# Calculate IRR (approx)
# IRR is the discount rate that makes NPV = 0
# Using Newton's method for approximation

def calculate_npv_at_rate(rate, cfs):

    return sum(cf["Net_Cash_Flow"] / ((1 + rate)**cf["Year"]) for cf in cfs)

# Binary search for IRR
low, high = 0.0, 1.0
irr = None
for _ in range(100):
    mid = (low + high)/2
    npv_at_mid = calculate_npv_at_rate(mid, cash_flows)
    if abs(npv_at_mid) < 1000: #Close enough 
        irr = mid 
        break
    if npv_at_mid > 0:
        low = mid
    else:
        high = mid 

print(f"\n YEAR-BY-YEAR CASH FLOWS PROJECTIONS:")
print(cash_flow_df.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))

print(f" NPV SUMMARY: ")
print(f" Total CapEX (Year 0): ${-total_capex:,.0f}")
print(f"PV of future cash flows: ${cash_flow_df[cash_flow_df['Year'] > 0]['Present_Value'].sum():,.0f}")
print(f"NET PRESENT VALUE: ${npv:,.0f}")
if irr:
    print(f"Internal Rate of Return (IRR): {irr*100:.1f}%")

if npv > 0:
    print(f"\n✓ PROJECT IS FINANCIALLY VIABLE (NPV > 0)")
    print(f"  Creates ${npv:,.0f} in present value over {years} years")
else:
    print(f"\n✗ PROJECT IS NOT VIABLE (NPV < 0) for a {years}-year horizon")

'''
PAYBACK PERIOD ANALYSIS
'''
cumulative_cash_flow = -total_capex
payback_period = None

for year in range(1, years + 1):
    annual_cf = cash_flow_df[cash_flow_df['Year'] == year]['Net_Cash_Flow'].iloc[0]
    cumulative_cash_flow += annual_cf

    print(f" End of Year {year}: Cumulative Cash Flow: ${cumulative_cash_flow:,.0f}")

    if cumulative_cash_flow >= 0 and payback_period is None:
        # Interpolate to find exact payback period
        prev_cf = cumulative_cash_flow - annual_cf
        fraction = abs(prev_cf) / annual_cf
        payback_period = year - 1 + fraction

if payback_period: 
    print(f"\n Payback Period: {payback_period:.2f} years")

    if payback_period < 2: 
        print(f" Excellent Payback (< 2 years)")
    elif payback_period <3:
        print(f" Good Payback (< 3 years)")

    else: 
        print(f" Acceptable Payback")
else: 
    print(f" \n Payback not achieved within {years} -- year period")


'''
ROI CALCUALTION
'''
total_benefit= cash_flow_df[cash_flow_df['Year'] > 0]['Net_Cash_Flow'].sum()

roi = ((total_benefit - total_capex) / total_capex) * 100 

print(f'\n RETURN ON INVESTMENT (ROI)')
print(f" Total Investment: ${total_capex:,.0f}")
print(f" Total {years} -- year benefit: ${total_benefit:,.0f}")
print(f" Net Benefit: ${total_benefit - total_capex:,.0f}")
print(f" ROI: {roi:.1f} % ")
print(f'Annualized ROI: {roi/years:.1f}%/year')

'''
Risk Adjustments and Sensitivity Analysis 
'''
print(f" RISK-ADJUSTED SCENARIOS")

scenarios = {
    'Base Case': {
        'volume_growth': 0.03,
        'cost_inflation': 0.02,
        'resale_price_factor': 1.0
    },
    'Conservative': {
        'volume_growth': 0.0,
        'cost_inflation': 0.04,
        'resale_price_factor': 0.9
    },
    "Optimistic": {
        'volume_growth': 0.05,
        'cost_inflation': 0.01,
        'resale_price_factor': 1.1
    }
}

scenario_results = []

for scenario_name, params, in scenarios.items():
    # Recalculating NPV for each scenario
    scenarios_cfs = []

    for year in range(years + 1):
        if year == 0:
            cf = -total_capex

        else: 
            volume = total_returns * ((1 + params['volume_growth']) ** year)
            revenue = (total_gross_revenue * params['resale_price_factor'] * 
                       ((1 + params['volume_growth']) ** year))
            opex = total_operating_cost * ((1 + params['volume_growth']) ** year) * ((1 + params['cost_inflation']) ** year)
            cf = revenue - opex 

        pv = cf / ((1 + discount_rate) ** year)
        scenarios_cfs.append(pv)

    scenario_npv = sum(scenarios_cfs)

    scenario_results.append({
        'Scenario': scenario_name,
        "NPV": scenario_npv,
        "Volume_Growth": params["volume_growth"],
        "Cost_Inflation": params["cost_inflation"],
        "Price_Factor": params["resale_price_factor"]
    })

    print(f" \n {scenario_name}")
    print(f" Volume Growth: {params['volume_growth']*100:.2f}%")
    print(f" Cost Inflation: {params['cost_inflation']*100:.2f}%")
    print(f" Resale Price Factor: {params['resale_price_factor']:.2f}")
    print(f" NPV: ${scenario_npv:,.0f}")

scenario_results_df = pd.DataFrame(scenario_results)

# Saving all Financial Results 

print(f"\n SAVING FINANCIAL ANALYSIS RESULTS")

#Saving Cash FLows

cash_flow_df.to_csv('outputs/financial_cash_flows.csv', index = False )
print(f" - Cash flow projections saved to outputs/financial_cash_flows.csv")

# Saving Scenario Results 
scenario_results_df.to_csv('outputs/financial_scenarios.csv', index = False)
print(f" - Scenario results saved to outputs/financial_scenarios.csv")

# Save Summary 
financial_summary = {
    "Analysis_Date": datetime.now().strftime("%Y-%m-%d"),
    "Current_Annual_Recovery": current_annual_recovery,
    "Proposed_Annual_Recovery": proposed_net_recovery,
    "Incremental_Annual_Value": incremental_annual_value,
    "Improvement_Percentage": improvement_pct * 100,  # Convert to percentage value
    "Total_Capex": total_capex,
    "NPV_3Year": npv,
    "IRR": irr if irr else 0,
    'Payback_Period_Years': payback_period if payback_period else 0.0,
    "ROI_Percentage": roi,
    "Annualized_ROI_Percentage": roi/years,
    "Discount_Rate": discount_rate,
    "Num_Facilities": num_facilities,
    "Facilities_Opened": facilities_opened,
}

financial_summary_df = pd.DataFrame([financial_summary])
financial_summary_df.to_csv('outputs/financial_summary.csv', index = False)

print(f" - Financial summary saved to outputs/financial_summary.csv")

