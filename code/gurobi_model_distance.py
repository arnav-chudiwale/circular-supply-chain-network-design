import gurobipy as gp
from gurobipy import GRB
import pickle 
import pandas as pd 
from datetime import datetime 

print('GUROBI MODEL #1 - DISTANCE MINIMIZATION')
print('Objective: Minimize total weighted distance (validate ArcGIS)')

#Load data 
with open('data/gurobi_data_package.pkl', 'rb') as f:
    data = pickle.load(f)

stores = data['stores']
facilities = data['facilities']
supply = data['supply']
distance = data['distance']
capacity = data['capacity']

print(f" \n Loaded Data: ")
print(f" Stores: {len(stores)}")
print(f" Facilities: {len(facilities)}")
print(f" Total Supply of devices to be refurbished: {sum(supply.values()):,} units/year")

p = 2
print(f" \n Constraint: Open exactly {p} facilities")

#Creating model
model = gp.Model("Facility_Location_Distance_Minimization")

#Decision Variables

print("\n Creating Decision Variables...")
# y[j] = 1 if facility j is opened 
y = {}
for j in facilities: 
    y[j] = model.addVar(vtype=GRB.BINARY, name=f"open_{j}")


# x[i,j] = 1 if store i is assigned to facility j 
x = {}
for i in stores:
    for j in facilities: 
        x[i,j] = model.addVar(vtype=GRB.BINARY, name=f"assign_{i}_to_{j}")

print(f" Created {len(facilities)} binary facility variables")
print(f" Created {len(stores)*len(facilities)} binary assignment variables")

#Objective Function: Minimize total weighted distance

print("\n Setting Objective Function: Minimize total weighted distance...")

objective = gp.quicksum(
    x[i,j] * supply[i] * distance[i,j]
    for i in stores 
    for j in facilities 
)

model.setObjective(objective, GRB.MINIMIZE)
print(" Objective function set")

#Constraints 
print("\n Adding Constraints...")

# 1. Each store assigned to exactly one facility
for i in stores:
    model.addConstr(
        gp.quicksum(x[i,j] for j in facilities) == 1,
        name = f"assign_{i}"
    )
print(f" Added {len(stores)} assignment constraints")

#2. Can only assign to open facilities (big-M constraint)
for i in stores:
    for j in facilities: 
        model.addConstr(
            x[i,j] <= y[j],
            name = f"link_{i}_{j}"
        )
print(f" Added {len(stores)*len(facilities)} linking constraints")

#3. Capacity Constraints
for j in facilities: 
    model.addConstr(
        gp.quicksum(x[i,j] * supply[i] for i in stores) <= capacity[j],
        name = f"capacity_{j}"
    )
print(f" Added {len(facilities)} capacity constraints")

# 4. Open exactly p facilities 
model.addConstr(
    gp.quicksum(y[j] for j in facilities) == p,
    name="facility_count"
)
print(f" Added constraint: Open exactly {p} facilities")

#Solve
print("\n Solving model...")
start_time = datetime.now()
model.optimize()
end_time = datetime.now()
solve_time = (end_time - start_time).total_seconds()

#Results
if model.Status == GRB.OPTIMAL:
    print(f"\n Optimal solution found in {solve_time:.2f} seconds")
    print(f" Optimal Objective (Total Weighted Distance): {model.ObjVal:.2f}")

    #EXTRACT CHOSEN FACILITY AND ASSIGNMENTS
    chosen_facilities = []
    print("\n Chosen Facilities:")
    for j in facilities:
        if y[j].X > 0.5: # binary variable, so >0.5 means it's chosen
            chosen_facilities.append(j)
            facility_info = data['facilities_df'][data['facilities_df']['Facility_ID'] == j].iloc[0]
            print(f"\n {j}: {facility_info['Name']}")
            print(f" Location: ({facility_info['City']})")
            print(f" Capacity: {capacity[j]:,} units/year")

    #Extracting assignments and calculating metrics
    print(f"\n Store Assignments by facility:")
    assignments = []
    facility_stats = {}

    for j in chosen_facilities:
        assigned_stores = []
        total_supply_j = 0
        total_weighted_dist_j = 0 

        for i in stores:
            if x[i,j].X > 0.5: # store i assigned to facility j
                assigned_stores.append(i)
                total_supply_j += supply[i]
                total_weighted_dist_j += supply[i] * distance[i,j]
                
                # Saving for export
                assignments.append({
                    'Store_ID': i,
                    "Facility_ID": j,
                    "Supply": supply[i],
                    "Distance_Miles": distance[i,j],
                    "Weighted_Distance": supply[i] * distance[i,j]
                })

        avg_distance = total_weighted_dist_j / total_supply_j if total_supply_j > 0 else 0
        utilization = (total_supply_j / capacity[j])*100

        facility_stats[j] = {
            'Num_Stores': len(assigned_stores),
            'Total_Supply': total_supply_j,
            'Total_Weighted_Distance': total_weighted_dist_j,
            'Average_Distance': avg_distance,
            'Utilization_pct': utilization
        }

        facility_info = data['facilities_df'][data['facilities_df']['Facility_ID'] == j].iloc[0]
        print(f" \n {j}: {facility_info['Name']}")
        print(f" Stores Assigned: {len(assigned_stores)}")
        print(f" Total Supply Assigned: {total_supply_j:,} units/year")
        print(f" Total Weighted Distance: {total_weighted_dist_j:.2f}")
        print(f" Average Distance: {avg_distance:.2f} miles")
        print(f" Utilization: {utilization:.2f}%")

    #Overall Statistics
    print("\n Network Performance Statistics:")
    total_supply_served = sum(supply.values())
    avg_weighted_distance = model.ObjVal / total_supply_served if total_supply_served > 0 else 0

    print(f" Total Supply Served: {total_supply_served:,} units/year")
    print(f" Average Weighted Distance: {avg_weighted_distance:.2f} miles")
    print(f" Total Weighted Distance: {model.ObjVal:.2f} miles*units/year")
    print(f" Number of Facilities Opened: {len(chosen_facilities)}")

    #Saving Results 
    print("\n Saving results")

    #Saving Assignments 
    assignments_df = pd.DataFrame(assignments)
    assignments_df.to_csv('outputs/gurobi_distance_minimization_assignments.csv', index=False)
    print(f" Saved store assignments to 'outputs/gurobi_distance_minimization_assignments.csv'")

    #Saving Facility Stats 
    facility_stats_df = pd.DataFrame(facility_stats).T
    facility_stats_df.to_csv('outputs/gurobi_distance_minimization_facility.csv', index = False)
    print(" Saved facility performance statistics to 'outputs/gurobi_distance_minimization_facility.csv'")

    #Save solution summary 
    summary = {
        'model': "Distance Minimization",
        'objective': "Minimize total weighted distance",
        "num_facilities": len(chosen_facilities),
        "facilities_opened": ','.join(chosen_facilities),
        "total_weighted_distance": model.ObjVal,
        "average_weighted_distance": avg_weighted_distance,
        "solve_time_seconds": solve_time,
        'optimal': model.Status == GRB.OPTIMAL
    }

    summary_df = pd.DataFrame([summary])
    summary_df.to_csv('outputs/gurobi_distance_minimization_summary.csv', index=False)
    print(" Saved solution summary to 'outputs/gurobi_distance_minimization_summary.csv'")

    # =============================================================================
    # COMPARISON WITH ARCGIS (if available)
    # =============================================================================
    
    if 'arcgis_facilities_df' in data:
        print("\n" + "="*70)
        print("COMPARISON WITH ARCGIS SOLUTION")
        print("="*70)
        
        # ArcGIS facilities with DemandCount > 0 were actually used/chosen
        arcgis_df = data['arcgis_facilities_df']
        arcgis_chosen = arcgis_df[arcgis_df['DemandCount'] > 0]['Name'].tolist()
        
        # Convert Gurobi facility IDs to names for comparison
        facilities_df = data['facilities_df']
        gurobi_chosen_names = [
            facilities_df[facilities_df['Facility_ID'] == fac]['Name'].iloc[0]
            for fac in chosen_facilities
        ]
        
        print(f"\nArcGIS chose: {', '.join(arcgis_chosen)}")
        print(f"Gurobi chose: {', '.join(gurobi_chosen_names)}")
        
        if set(arcgis_chosen) == set(gurobi_chosen_names):
            print("\n✓ EXACT MATCH! Gurobi validates ArcGIS solution.")
        else:
            print("\n- Different facilities chosen")
            print("  This could be due to:")
            print("  - Different distance calculations (network vs straight-line)")
            print("  - Numerical precision differences")
    
    print("\n" + "="*70)
    print("✅ MODEL #1 COMPLETE")
    print("="*70)
    
else:
    print("\n✗ NO OPTIMAL SOLUTION FOUND")
    print(f"Model status: {model.status}")
    if model.status == GRB.INFEASIBLE:
        print("\nModel is INFEASIBLE. Possible causes:")
        print("  - Capacity constraints too tight")
        print("  - Number of facilities (p) too small")
        model.computeIIS()
        model.write("outputs/model_distance_infeasible.ilp")
        print("  - Wrote IIS to outputs/model_distance_infeasible.ilp")