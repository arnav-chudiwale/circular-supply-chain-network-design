import gurobipy as gp 
from gurobipy import GRB
import pickle 
import pandas as pd
from datetime import datetime

print('GUROBI MODEL #2: TOTAL COST MINIMIZATION')
print('Objective: Minimize fixed costs + transportation costs')

#Load data

with open("data/gurobi_data_package.pkl", 'rb') as f:
    data = pickle.load(f)

stores = data['stores']
facilities = data['facilities']
supply = data['supply']
distance = data['distance']
fixed_cost = data['fixed_cost']
capacity = data['capacity']
transport_cost_per_mile = data['transport_cost_per_mile']

print(f" Loaded data:")
print(f" Stores: {len(stores)}")
print(f" Facilities: {len(facilities)}")
print(f" Total Supply of devices to be refurbished: {sum(supply.values()):,} units/year")
print(f" Transport cost per mile: ${transport_cost_per_mile:.2f}")

#Show cost range 
print(f" \n Fixed Cost Range:")
for j in facilities:
    facility_info = data['facilities_df'][data['facilities_df']['Facility_ID'] == j].iloc[0]
    print(f" {j}: ${fixed_cost[j]:,}/year - {facility_info['Name']}")

p = 2
print(f" \n Constraint: Open exactly {p} facilities")

#Creating model 

model = gp.Model("Facility_Location_Cost_Minimization") 

#Decision variables
print("\n Creating decision variables")

y = {}
for j in facilities: 
    y[j] = model.addVar(vtype=GRB.BINARY, name = f"open_{j}")

x={}
for i in stores: 
    for j in facilities:
        x[i,j] = model.addVar(vtype=GRB.BINARY, name = f"assign_{i}_to_{j}")

print(f" Created {len(facilities)} binary facility variables")
print(f" Created {len(stores)*len(facilities)} binary assignment variables")

#Objective function: Minimize total cost = fixed cost + transport cost
print("\n Setting Objective Function: Minimize total cost (fixed + transport)")

#Fixed Cost 
fixed_cost_expr = gp.quicksum(
    y[j] * fixed_cost[j] for j in facilities
)

#Transport Cost
transport_cost_expr = gp.quicksum(
    x[i,j] * supply[i] * distance[i,j] * transport_cost_per_mile
    for i in stores 
    for j in facilities 
)

#Total Cost 
total_cost_expr = fixed_cost_expr + transport_cost_expr

model.setObjective(total_cost_expr, GRB.MINIMIZE)
print(" Objective: Minimize total cost set")

#Constraints
print("\n Adding Constraints...")

#1. Each stores assigned to exactly one facility 
for i in stores:
    model.addConstr(
        gp.quicksum(x[i,j] for j in facilities) == 1,
        name = f"assign_store_{i}"
    )
print(f" Added {len(stores)} assignment constraints")

#2. Linking constraints: can only assign to open facilities
for i in stores:
    for j in facilities:
        model.addConstr(
            x[i,j] <= y[j],
            name = f"link_{i}_{j}"
        )
print(f" Added {len(stores)*len(facilities)} linking constraints")

#3. Capacity constraints
for j in facilities:
    model.addConstr(
        gp.quicksum(x[i,j] * supply[i] for i in stores) <= capacity[j],
        name = f"capacity_{j}"
    )
print(f" Added {len(facilities)} capacity constraints")

#4. Facility count constraint: Open exactly p facilities
model.addConstr(
    gp.quicksum(y[j] for j in facilities) == p,
    name = "facility_count"
)
print(" Added facility count constraint")

#Solve 
print("\n Solving...")
start_time = datetime.now()
model.optimize()
end_time = datetime.now()
solve_time = (end_time - start_time).total_seconds()

#Extract and display results
if model.Status == GRB.OPTIMAL:
    print ("\n Optimal Solution Found!")
    print(f" \n Solve Time: {solve_time:.2f} seconds")

    #Calulate cost components
    total_fixed = sum(y[j].X * fixed_cost[j] for j in facilities)
    total_transport = sum(x[i,j].X * supply[i] * distance[i,j] * transport_cost_per_mile for i in stores for j in facilities)
    total_cost = total_fixed + total_transport 

    print("Cost Breakdown:")
    print(f" Total Fixed Cost: ${total_fixed:,.2f}")
    print(f" Total Transport Cost: ${total_transport:,.2f}")
    print(f" Total Annual Cost: ${total_cost:,.2f}")
    print(f" (Model Objective Value: ${model.ObjVal:,.2f})")

    #Extracting Chosen Facility 
    chosen_facilities = []
    for j in facilities:
        if y[j].X > 0.5:
            chosen_facilities.append(j)

    #Assignments and facility stats
    print(f" CHOSEN FACILITIES AND FACILITY LEVEL ANALYSIS:")
    assignments = []
    facility_stats = {}

    for j in chosen_facilities:
        total_supply_j = 0
        total_weighted_dist_j = 0
        num_stores_j = 0

        for i in stores: 
            if x[i,j].X > 0.5:
                num_stores_j += 1
                total_supply_j += supply[i]
                total_weighted_dist_j += supply[i] * distance[i,j]

                assignments.append({
                    "Store_ID": i,
                    "Facility_ID": j,
                    "Supply": supply[i],
                    "Distance_Miles": distance[i,j],
                    "Weighted_Distance": supply[i] * distance[i,j],
                    'Transport_Cost': supply[i] * distance[i,j] * transport_cost_per_mile
                })
        
        avg_distance = total_weighted_dist_j / total_supply_j if total_supply_j > 0 else 0
        utilization = (total_supply_j / capacity[j])*100
        facility_transport_cost = total_weighted_dist_j * transport_cost_per_mile

        facility_stats[j] = {
            "Num_Stores": num_stores_j,
            "Total_Supply": total_supply_j,
            "Utilization_Pct": utilization,
            "Avg_Distance": avg_distance,
            "Total_Weighted_Distance": total_weighted_dist_j,
            "Fixed_Cost": fixed_cost[j],
            "Transport_Cost": facility_transport_cost,
            "Total_Cost": fixed_cost[j] + facility_transport_cost
        }

        facility_info = data['facilities_df'][data['facilities_df']['Facility_ID'] == j].iloc[0]
        print(f"\n {j}: {facility_info['Name']}")
        print(f" Stores Assigned: {num_stores_j}")
        print(f" Total Supply Assigned: {total_supply_j:,} units/year")
        print(f" Average Distance: {avg_distance:.2f} miles")
        print(f" Fixed Cost: ${fixed_cost[j]:,}/year")
        print(f" Transport Cost: ${facility_transport_cost:,.2f}/year")
        print(f" Total Cost: ${fixed_cost[j] + facility_transport_cost:,.2f}/year")

    #Overall metrics
    total_supply_served = sum(supply.values())
    total_weighted_distance = sum(
        x[i,j].X * supply[i] * distance[i,j] for i in stores for j in facilities
    )
    avg_weighted_distance = total_weighted_distance / total_supply_served if total_supply_served > 0 else 0

    print(f"\n NETWORK PERFORMANCE:")
    print(f" Facilities Opened: {len(chosen_facilities)}")
    print(f" Total Supply Served: {total_supply_served:,} units/year")
    print(f" Average Weighted Distance: {avg_weighted_distance:.2f} miles")
    print(f" Total Weighted Distance: {total_weighted_distance:.2f} miles*units/year")
    print(f" \n Fixed Cost Range of Opened Facilities: ${total_fixed:,.2f}")
    print(f" Transport Cost: ${total_transport:,.2f}")
    print(f" Total Annual Cost: ${total_cost:,.2f}")

    #Comparison to distance minimization model
    print(f"\n COMPARISON TO DISTANCE MINIMIZATION MODEL:")

    try: 
        distance_summary = pd.read_csv("outputs/gurobi_distance_minimization_summary.csv")
        distance_facilities_str = distance_summary['facilities_opened'].iloc[0]
        # Split the comma-separated string into a list
        distance_facilities = distance_facilities_str.split(',')
        distance_objective = distance_summary['total_weighted_distance'].iloc[0]

        print(f"\n Distance Model (minimize distance only):")
        print(f" Facilities: {', '.join(distance_facilities)}")
        print(f" Total Weighted Distance: {distance_objective:,.2f} miles*units/year")

        #Calculate cost if we used distance model's solution
        distance_model_fixed_cost = sum(fixed_cost[j] for j in distance_facilities)
        distance_model_transport_cost = distance_objective * transport_cost_per_mile
        distance_model_total_cost = distance_model_fixed_cost + distance_model_transport_cost
        
        print(f" Would cost: ${distance_model_total_cost:,.2f}")
        
        print(f"\nCost Model (minimize total cost):")
        print(f" Facilities: {', '.join(chosen_facilities)}")
        print(f" Total Weighted Distance: {total_weighted_distance:,.2f} miles*units/year")
        print(f" Total cost: ${total_cost:,.2f}")
        
        if distance_model_total_cost > total_cost:
            savings = distance_model_total_cost - total_cost
            pct_savings = (savings / distance_model_total_cost) * 100
            print(f"\n Savings from cost optimization: ${savings:,.2f} ({pct_savings:.1f}% reduction)")
            print(f" Achieved by accepting {total_weighted_distance - distance_objective:,.0f} more ton-miles")
        else:
            print(f"\n Distance model happened to also be cost-optimal")
            
    except Exception as e:
        print(f"(Warning: Could not load distance model results for comparison - {str(e)})")
    
    # =============================================================================
    # SAVE RESULTS
    # =============================================================================
    
    print("\n" + "="*70)
    print("SAVING RESULTS...")
    print("="*70)
    
    assignments_df = pd.DataFrame(assignments)
    assignments_df.to_csv('outputs/gurobi_cost_assignments.csv', index=False)
    print("Saved: outputs/gurobi_cost_assignments.csv")
    
    facility_stats_df = pd.DataFrame(facility_stats).T
    facility_stats_df.to_csv('outputs/gurobi_cost_facility_stats.csv')
    print("Saved: outputs/gurobi_cost_facility_stats.csv")
    
    summary = {
        'model': 'Cost Minimization',
        'objective': 'Minimize total cost',
        'num_facilities': len(chosen_facilities),
        'facilities_opened': ', '.join(chosen_facilities),
        'total_fixed_cost': total_fixed,
        'total_transport_cost': total_transport,
        'total_annual_cost': total_cost,
        'total_weighted_distance': total_weighted_distance,
        'avg_weighted_distance': avg_weighted_distance,
        'solve_time_seconds': solve_time,
        'optimal': True
    }
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv('outputs/gurobi_cost_summary.csv', index=False)
    print("Saved: outputs/gurobi_cost_summary.csv")
    
    print("\n" + "="*70)
    print("✅ MODEL #2 COMPLETE")
    print("="*70)
    print("\nKey Insight:")
    print("  Cost-optimal solution may use DIFFERENT facilities than")
    print("  distance-optimal solution due to fixed cost differences!")
    
else:
    print("\nNO OPTIMAL SOLUTION FOUND")
    print(f"Model status: {model.status}")


