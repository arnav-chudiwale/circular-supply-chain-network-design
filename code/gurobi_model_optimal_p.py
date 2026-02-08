import gurobipy as gp 
from gurobipy import GRB
import pickle 
import pandas as pd 
from datetime import datetime
import matplotlib.pyplot as plt

print(f" GUROBI MODEL #3 - OPTIMAL NUMBER OF FACILITIES")
print(f" Objective: Find optimal p (number of facilities) to minimize total cost")

#Loading data
with open('data/gurobi_data_package.pkl', 'rb') as f:
    data = pickle.load(f)

stores = data["stores"]
facilities = data["facilities"]
distance = data["distance"]
supply = data['supply']
capacity = data["capacity"]
fixed_cost = data["fixed_cost"]
transport_cost_per_mile = data["transport_cost_per_mile"]
handling_cost_per_unit = data["handling_cost_per_unit"]
pickup_dropoff_fee = data["pickup_dropoff_fee"]
facilities_df = data["facilities_df"]

# Create mapping of facility ID to Name and City
facility_details = dict(zip(facilities_df['Facility_ID'], 
                            facilities_df[['Name', 'City']].itertuples(index=False, name=None)))

total_supply = sum(supply.values())
total_capacity = sum(capacity.values())

print ("\n Loaded Data:")
print(f" Stores: {len(stores)}")
print(f" Facilities: {len(facilities)}")
print(f" Total Supply: {total_supply:,} units")
print(f" Total Capacity: {total_capacity:,} units")

#Determine feasible range for p 

# Minimum p: Need enough capacity to meet supply from stores 
min_p = 1 
cumulative_capacity = 0 
sorted_facilities_by_capacity = sorted(facilities, 
                                       key=lambda j: capacity[j],
                                       reverse = True)

for i, j in enumerate(sorted_facilities_by_capacity, 1):
    cumulative_capacity += capacity[j]
    if cumulative_capacity >= total_supply:
        min_p = i 
        break

# Maximum p: Cannot open more facilities than available
max_p = len(facilities)

print(f"\n Feasible range for p (number of facilities to open): {min_p} to {max_p}")

# Solving for each value of p in the feasible range

results = []
print("Solving for each p value in the feasible range...")

for p in range(min_p, max_p + 1):
    print(f"\n Solving for p= {p}")

    # Create Model
    model = gp.Model(f"Facility_Location_p_{p}")
    model.setParam('OutputFlag', 0) # Supressing output for cleaner results

    # Decision Variables
    y = {}
    for j in facilities: 
        y[j] = model.addVar(vtype=GRB.BINARY, name=f"open_{j}")

    x = {}
    for i in stores: 
        for j in facilities: 
            x[i,j] = model.addVar(vtype=GRB.BINARY, name=f"assign_{i}_to_{j}")

    
    #Objective : Minimize total cost 
    fixed_cost_expr = gp.quicksum(fixed_cost[j] * y[j] for j in facilities)
    pickup_dropoff_expr = gp.quicksum(pickup_dropoff_fee * y[j] for j in facilities)
    handling_cost_expr = gp.quicksum(
        supply[i] * x[i,j] * handling_cost_per_unit for i in stores for j in facilities
    )
    transport_cost_expr = gp.quicksum(
        supply[i] * x[i,j] * distance[i,j] * transport_cost_per_mile for i in stores for j in facilities
    )

    total_cost = fixed_cost_expr + pickup_dropoff_expr + handling_cost_expr + transport_cost_expr

    model.setObjective(total_cost, GRB.MINIMIZE)

    #Constraints 
    # 1. Assignment
    for i in stores:
        model.addConstr(
            gp.quicksum(x[i,j] for j in facilities) == 1,
            name = f"assign_store_{i}"
        )

    # 2. Linking 
    for i in stores:
        for j in facilities:
            model.addConstr(
                x[i,j] <= y[j],
                name = f"link_{i}_{j}"
            )
    # 3. Capacity
    for j in facilities:
        model.addConstr(
            gp.quicksum(x[i,j] * supply[i] for i in stores) <= capacity[j] * y[j],
            name = f"capacity_{j}"
        )

    # 4. Number of facilities = p 
    model.addConstr(
        gp.quicksum(y[j] for j in facilities) == p,
        name = "num_facilities"
    )

    #Solve
    start_time = datetime.now()
    model.optimize()
    end_time = datetime.now()

    solve_time = (end_time - start_time).total_seconds()

    #Extract Results
    if model.Status == GRB.OPTIMAL:

        # Get chosen facilities 
        chosen = [j for j in facilities if y[j].X > 0.5]
        
        # Create detailed facility info string
        facility_info = ', '.join([f"{j} ({facility_details[j][0]}, {facility_details[j][1]})" for j in chosen])
        facility_ids_only = ','.join(chosen)

        # Calculate cost components 
        total_fixed = sum(y[j].X * fixed_cost[j] for j in facilities)
        total_pickup_dropoff = sum(y[j].X * pickup_dropoff_fee for j in facilities)
        total_handling = sum(x[i,j].X * supply[i] * handling_cost_per_unit for i in stores for j in facilities)
        total_transport = sum(x[i,j].X * supply[i] * distance[i,j] * transport_cost_per_mile for i in stores for j in facilities)

        total_cost_val = total_fixed + total_pickup_dropoff + total_handling + total_transport

        # Calculate distance 
        total_weighted_distance = sum(
            x[i,j].X * distance[i,j] * supply[i]
            for i in stores for j in facilities)
        
        avg_distance = total_weighted_distance / total_supply

        # Calculate utilization
        total_capacity_opened = sum(capacity[j] for j in chosen)
        avg_utilization = (total_supply / total_capacity_opened) * 100 

        print(f" Solved in {solve_time:.2f} seconds")
        print(f' Facilities opened: {facility_info}')
        print(f" Facility Fixed Cost: ${total_fixed:,.2f}")
        print(f" Pickup/Drop-off Fee: ${total_pickup_dropoff:,.2f}")
        print(f" Handling Cost: ${total_handling:,.2f}")
        print(f" Transport Cost: ${total_transport:,.2f}")
        print(f" Total Cost: ${total_cost_val:,.2f}")
        print(f" Average Distance: {avg_distance:.2f} miles")
        print(f" Average Utilization: {avg_utilization:.2f}%")

        results.append({
            'p': p,
            'facilities_opened_ids': facility_ids_only,
            'facilities_opened': facility_info,
            'total_fixed_cost': total_fixed,
            'total_pickup_dropoff_fee': total_pickup_dropoff,
            'total_handling_cost': total_handling,
            'total_transport_cost': total_transport,
            'total_cost': total_cost_val,
            'total_weighted_distance': total_weighted_distance,
            'avg_distance': avg_distance,
            'avg_utilization': avg_utilization,
            'total_capacity_opened': total_capacity_opened,
            'solve_time': solve_time,
            'status': "Optimal"

        })

    else:
        print(f" No solutipon found (Status : {model.Status})")
        results.append({
            'p': p,
            'status': 'Infeasible or No Solution' if model.Status == GRB.INFEASIBLE else 'No Solution',
            'total_cost': float('inf')
        })

# Analyse results across all p values 

results_df = pd.DataFrame(results)
results_df = results_df[results_df['status'] == 'Optimal'] # keep only feasible solutions\

if len(results_df) == 0:
    print("\n NO FEASIBLE SOLUTION FOUND")
    print(' Check capacity constraints and problem parameters')

    exit(1)

print("\n Comparison across all p values:")

for _, row in results_df.iterrows():
    print(f"\n p = {row['p']}:")
    print(f" Facilities Opened: {row['facilities_opened']}")
    print(f" Fixed Cost: ${row['total_fixed_cost']:,.2f}")
    print(f" Transport Cost: ${row['total_transport_cost']:,.2f}")
    print(f" Total Cost: ${row['total_cost']:,.2f}")
    print(f" Average Distance: {row['avg_distance']:.2f} miles")

# Finding optimal p 
optimal_row = results_df.loc[results_df['total_cost'].idxmin()]
optimal_p = int(optimal_row['p'])

print(f"\n Optimal solution found")
print(f"\n Optimal number of facilities for refurbishment: p* = {optimal_p}")
print(f" Facilities to open: {optimal_row['facilities_opened']}")
print(f" Total Annual Cost: ${optimal_row['total_cost']:,.2f}")
print(f" Fixed Cost: ${optimal_row['total_fixed_cost']:,.2f}")
print(f" Transport Cost: ${optimal_row['total_transport_cost']:,.2f}")
print(f" Average Distance per unit: {optimal_row['avg_distance']:.2f} miles")
print(f" Average Facility Utilization: {optimal_row['avg_utilization']:.2f}%")

# Marginal Analysis
print("\n MARGINAL COST ANALYSIS:")

print(f" \n Cost reduction from opening additional facilities")

for i in range(len(results_df) - 1):
    current = results_df.iloc[i]
    next_val = results_df.iloc[i + 1]

    marginal_cost = next_val['total_cost'] - current['total_cost']
    marginal_pct = (marginal_cost/current['total_cost']) * 100 

    print(f" p={int(current['p'])} --> p={int(next_val['p'])}")
    if marginal_cost < 0:
        print(f" Save ${abs(marginal_cost):,.2f} ({abs(marginal_pct):1f}% reduction)")
    else: 
        print(f" Cost increase by ${marginal_cost:,.0f} ({marginal_pct:.1f})")
        print(f" Opening Facility #{int(next_val['p'])} does not provide cost savings compared to {int(current['p'])}")


'''
VISUALIZATION: COST VS NUMBER OF FACILITIES
'''
print("\n Creating visualizations")

fig, axes = plt.subplots(2,2, figsize=(14,10))
fig.suptitle('Facility Location Analysis - Impact of number of facilities (p)',
             fontsize = 16, fontweight = 'bold')

#Plot #1 = Total Cost vs p 
ax1= axes[0,0]
ax1.plot(results_df['p'], results_df['total_cost'], 'o-', linewidth = 2, markersize = 8, color = 'lightcoral')
ax1.axvline(optimal_p, color = 'red', linestyle = '--', alpha = 0.7, label = f"Optimal: p={optimal_p}")

# Add text labels on top of each data point
for idx, (p, cost) in enumerate(zip(results_df['p'], results_df['total_cost'])):
    ax1.text(p, cost, f'${cost:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold', 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7, edgecolor='black', linewidth=1))

ax1.set_title("Total Cost vs Number of Facilities (p)", fontsize = 12, fontweight = 'bold')
ax1.set_xlabel("Number of Facilities (p)", fontsize = 10, fontweight = 'bold')
ax1.set_ylabel("Total Annual Cost ($)", fontsize = 10, fontweight = 'bold')
ax1.grid(True, alpha = 0.3)
ax1.legend()
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:,.1f}M'))

# Plot #2 = Fixed Cost vs p 
ax2 = axes[0,1]
width = 0.6 
x_pos = results_df['p'].values
ax2.bar(x_pos, results_df['total_fixed_cost'], width, label = "Fixed Cost", color = 'lightblue', edgecolor='navy', linewidth=1.5)
ax2.axvline(optimal_p, color = 'red', linestyle = '--', alpha = 0.7, linewidth=2)
ax2.set_xlabel('Number of Facilities (p)', fontsize = 10, fontweight = 'bold')
ax2.set_ylabel('Fixed Cost ($)', fontsize = 10, fontweight = 'bold')
ax2.set_title('Fixed Cost vs Number of Facilities', fontsize = 12, fontweight = 'bold')
ax2.set_xticks(x_pos)
ax2.legend()
ax2.grid(True, alpha = 0.3, axis = 'y')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:,.0f}M'))

# Plot #3 = Average Distance vs p 
ax3 = axes[1,0]
ax3.plot(results_df['p'], results_df['avg_distance'], 's-', linewidth = 2, markersize = 8, color = 'mediumpurple')
ax3.axvline(optimal_p, color = 'red', linestyle = '--', alpha = 0.7, label = f"Optimal: p={optimal_p}")
ax3.set_xlabel("Number of facilities (p)", fontsize = 10, fontweight = 'bold')
ax3.set_ylabel("Average Distance (miles/unit)", fontsize = 10, fontweight = 'bold')
ax3.set_title("Service Distance vs Number of Facilities", fontsize = 12, fontweight = 'bold')
ax3.grid(True, alpha = 0.3)
ax3.legend()

# Plot #4 = Utilization vs p 
ax4 = axes [1,1]
ax4.plot(results_df['p'], results_df['avg_utilization'], '^-', linewidth = 2, markersize = 8, color = 'darkorange')
ax4.axvline(optimal_p, color = 'red', linestyle = '--', alpha = 0.7, label = f"Optimal: p={optimal_p}")
ax4.axhline(100, color = 'orange', linestyle = ':', alpha = 0.7, label = "100% Utilization")
ax4.set_xlabel("Number of facilities(p)", fontsize = 10, fontweight = 'bold')
ax4.set_ylabel("Average Utilization (%)", fontsize = 10, fontweight = 'bold')
ax4.set_title("Annual Facility Utilization vs Number of Facilities", fontsize = 12, fontweight = 'bold')
ax4.grid(True, alpha = 0.3)
ax4.legend()

plt.tight_layout()
plt.savefig('outputs/optimal_p_analysis.png', dpi = 300, bbox_inches = 'tight')
print(" Saved: outputs/optimal_p_analysis.png")


# Saving results 

results_df.to_csv('outputs/gurobi_optimal_p_results.csv', index = False)
print(" Saved: outputs/gurobi_optimal_p_results.csv")

#Saving optimal solution details 
optimal_summary = {
    'optimal_p': optimal_p,
    'facilities_opened_ids': optimal_row['facilities_opened_ids'],
    'facilities_opened': optimal_row['facilities_opened'],
    'total_annual_cost': optimal_row['total_cost'],
    'total_fixed_cost': optimal_row['total_fixed_cost'],
    'total_pickup_dropoff_fee': optimal_row['total_pickup_dropoff_fee'],
    'total_handling_cost': optimal_row['total_handling_cost'],
    'total_transport_cost': optimal_row['total_transport_cost'],
    'avg_distance_miles': optimal_row['avg_distance'],
    'avg_utilization_pct': optimal_row['avg_utilization'],
    'model': "Optimal p Determination"
}

optimal_summary_df = pd.DataFrame([optimal_summary])
optimal_summary_df.to_csv('outputs/gurobi_optimal_p_summary.csv', index = False)
print(" Saved: outputs/gurobi_optimal_p_summary.csv")

