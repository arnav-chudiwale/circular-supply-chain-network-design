import gurobipy as gp
from gurobipy import GRB

try:
    model = gp.Model("test")
    print("✓ Gurobi license is ACTIVE!")
    print(f"Gurobi version: {gp.gurobi.version()}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    print("Fix your Gurobi license before proceeding!")