import pandas as pd

print('DEFINING COST PARAMETERS')

#All values researched from industry data

cost_parameters = {
    'bulk_recycler_payout_per_unit': 22, #Industry standard e-waste payout

    #Proposed state - Recovery values per unit (net - after fees/refurbishment)
    'grade_a_resale_price': 400, 
    'grade_b_resale_price': 250, 
    'grade_c_parts_value': 50,

    #Processing costs
    'grade_a_handling_cost': 10, #Testing + data wipe + repackaging
    'grade_b_refurb_cost': 55, # Screen/battery replacement (industry average)
    'grade_c_processing_cost': 12, #disassembly labor

    #Facility costs (annual) - CALIFORNIA SPECIFIC
    'facility_fixed_cost_bayarea': 1050000, #Bay Area
    'facility_fixed_cost_la': 980000, #Los Angeles
    'facility_fixed_cost_san_diego': 920000, #San Deigo
    'facility_fixed_cost_central': 820000, #Central Valley (Frensco)
    'facility_fixed_cost_nevada': 720000, #Reno, NV (out of state)

    #Facility capacity (units/year)
    'facility_capacity_units': 25000, #Industry standard for smartphones

    #Transport (per mile per unit)
    'transport_cost_per_mile_per_unit': 0.08, # LTL freight CA rates 2024

    #Time value decay
    'value_decay_per_week': 4
}

params_df = pd.DataFrame([cost_parameters])

params_df.to_csv('data/cost_parameters.csv', index = False)

print("\n Cost parameters defined:")
print(f" Bulk Recycler Payout per Unit: ${cost_parameters['bulk_recycler_payout_per_unit']} per unit")
print(f" Grade A Net Recovery: ${cost_parameters['grade_a_resale_price']} per unit")
print(f" Grade B Net Recovery: ${cost_parameters['grade_b_resale_price']} per unit")
print(f" Grade C Parts Value: ${cost_parameters['grade_c_parts_value']} per unit")
print(f" Refurbishment Cost (Grade B): ${cost_parameters['grade_b_refurb_cost']} per unit")
print(f" Bay Area Facility: ${cost_parameters['facility_fixed_cost_bayarea']:,.2f} annually")
print(f" Los Angeles Facility: ${cost_parameters['facility_fixed_cost_la']:,.2f} annually")
print(f" San Diego Facility: ${cost_parameters['facility_fixed_cost_san_diego']:,.2f} annually")
print(f" Central Valley Facility: ${cost_parameters['facility_fixed_cost_central']:,.2f} annually")
print(f" Nevada Facility: ${cost_parameters['facility_fixed_cost_nevada']:,.2f} annually")
print(f" Facility Capacity: {cost_parameters['facility_capacity_units']} units/year")
print(f" Value Decay: ${cost_parameters['value_decay_per_week']} per week")

print("\n Cost parameters saved to data/cost_parameters.csv")