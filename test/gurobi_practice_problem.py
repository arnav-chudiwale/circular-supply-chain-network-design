import gurobipy as gp 
from gurobipy import GRB 

print("Practice problem: simple facility location problem")


#Problem Data
stores = ['S1', 'S2', 'S3']
facilities = ['F1', 'F2']

demand = {
    'S1': 100,
    'S2': 150,
    'S3': 200
}

#Distance Matrix (miles)
distance = {
    ('S1', 'F1'): 10,
    ('S1', 'F2'): 50,
    ('S2', 'F1'): 30,
    ('S2', 'F2'): 20,
    ('S3', 'F1'): 60,
    ('S3', 'F2'): 15
}

# Facility data
fixed_cost = {"F1": 5000, "F2": 3000}
capacity = {"F1": 300, "F2": 250}

transport_cost_per_mile = 0.1

print("\n Problem Setup")
print(f"Stores: {stores}")
print(f"Facilties: {facilities}")
print(f"Total Demand: {sum(demand.values())} units")

#Creating model 
model = gp.Model("Simple_Facility_Location")

#Decision Variables
# y[j] = 1 if facility j is opened, 0 otherwise
y = {}
for j in facilities:
    y[j] = model.addVar(vtype = GRB.BINARY, name=f"open_{j}")

# x[i,j] = 1 if store i is assigned to facility j
x={}
for i in stores:
    for j in facilities:
        x[i,j] = model.addVar(vtype=GRB.BINARY, name=f"assign_{i}_to{j}")

#Objective function: Minimize total cost 
#Total Cost = Fixed Cost + Transport Cost
model.setObjective(
    #Fixed Cost: sum of (open_j * fixed_cost_j)
    gp.quicksum(y[j] * fixed_cost[j] for j in facilities) + 
    #Transport Cost: sum of (assign_ij * demand_i * distance_ij * cost_per_mile)
    gp.quicksum(x[i,j] * demand[i] * distance[i,j] * transport_cost_per_mile for i in stores for j in facilities),

    GRB.MINIMIZE

)

#Constraints 

# 1. Each stores must be assigned to exactly one facility 
for i in stores:
    model.addConstr(
        gp.quicksum(x[i,j] for j in facilities) == 1,
        name = f"assign_store_{i}"
    )

# 2. Can only assign to open facilities (big-M constraint)
for i in stores:
    for j in facilities:
        model.addConstr(
            x[i,j] <= y[j],
            name = f"link_{i}_{j}"
        )

# 3. Capacity constraints 
for j in facilities:
    model.addConstr(
        gp.quicksum(x[i,j] * demand[i] for i in stores) <= capacity[j],
        name= f"capacity_{j}"
    )

#Solve
print('\n Solving...')
model.optimize()

#Results 
print("\Results:")

if model.Status == GRB.OPTIMAL:
    print(f"\n Optimal Solution found")
    print(f" Total Cost: ${model.ObjVal:.2f}")
    print("\n Facilities opened:")
    total_fixed_cost = 0
    for j in facilities:
        if y[j].X > 0.5: # Binary variable, so check if it's 1
            print(f" - {j} (Fixed Cost: ${fixed_cost[j]:,})")
            total_fixed_cost += fixed_cost[j]

    print(f"\n Total Fixed Cost: ${total_fixed_cost:,}")

    print('\n Stores Assigned:')
    total_transport_cost = 0
    for i in stores:
        for j in facilities:
            if x[i,j].X > 0.5: #Store i assigned to facility j
                transport = demand[i] * distance[i,j] * transport_cost_per_mile
                total_transport_cost += transport
                print(f" {i} ({demand[i]} units) -> {j}")
                print(f" Distance: {distance[i,j]} miles")
                print(f" Total Transport Cost: ${transport:.2f}\n")


    #Verify 
    print(f" \n Verification:")
    print(f" Total Fixed Cost: ${total_fixed_cost:.2f}")
    print(f" Total Transport Cost: ${total_transport_cost:.2f}")     
    print(f" Total Cost (Fixed + Transport): ${total_fixed_cost + total_transport_cost:.2f}")
    print(f" Model Objective Value: ${model.ObjVal:.2f}")

else: 
    print(f" No optimal solution found")
    print(f" Status: {model.Status}")