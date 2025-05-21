import gurobipy as gp
from gurobipy import GRB

def solve_binary_programming():
    # Create a new Gurobi model
    model = gp.Model("Binary Programming")

    # Create decision variables
    x1 = model.addVar(vtype=GRB.BINARY, name="x1")
    x2 = model.addVar(vtype=GRB.BINARY, name="x2")
    x3 = model.addVar(vtype=GRB.BINARY, name="x3")

    # Set the objective function
    model.setObjective(x1 + 2 * x2 + 3 * x3, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(x1 + x2 + x3 <= 2, "c1")
    model.addConstr(x1 - x2 >= 0, "c2")

    # Optimize the model
    model.optimize()

    # Check optimization result
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found!")
        print("Objective value: ", model.objVal)
        print("Solution:")
        for v in model.getVars():
            print(v.varName, "=", v.x)
    else:
        print("No solution found.")


# Solve the binary programming problem


solve_binary_programming()

