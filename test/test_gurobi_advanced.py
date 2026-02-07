import gurobipy as gp 
from gurobipy import GRB
import sys 

print("GUROBI ENVIRONMENT TEST")

try: 
    #Create test model 
    model = gp.Model("test")

    #Adding variables
    x = model.addVar(vtype=GRB.BINARY, name='x')
    y = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=10.0, name='y')

    #Setting objective
    model.setObjective(x+2*y, GRB.MAXIMIZE)

    #Adding constraints
    model.addConstr(x+y <= 5, 'c1')

    #Solve
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        print(" Gurobi working correctly.")
        print(f" Version: {gp.gurobi.version()}")
        print(f" Optimal Objective: {model.ObjVal}")
        print(f" Solution: x={x.X}, y={y.X}")

    else:
        print(" Model did not solve to optimality")
        print(f'status code: {model.Status}')

except Exception as e:
    print(f" Error: {e}")

print("\n Ready to build optimization models with Gurobi!")

