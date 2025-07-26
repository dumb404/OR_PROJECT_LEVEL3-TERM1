from pulp import *
import pandas as pd

# Define sources and destinations
sources = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6_Dummy']
destinations = ['D1', 'D1_Extra', 'D2', 'D2_Extra', 'D3', 'D3_Extra', 'D4', 'D4_Extra', 'D5', 'D5_Extra', 'D6']

# Cost matrix (6 sources x 11 destinations)
# Big M set to 1e4 to avoid numerical issues
M = 1e4
costs = {
    ('S1', 'D1'): 22.8, ('S1', 'D1_Extra'): 22.8, ('S1', 'D2'): 56.18, ('S1', 'D2_Extra'): 56.18,
    ('S1', 'D3'): 13.19, ('S1', 'D3_Extra'): 13.19, ('S1', 'D4'): 4.6, ('S1', 'D4_Extra'): 4.6,
    ('S1', 'D5'): 28.31, ('S1', 'D5_Extra'): 28.31, ('S1', 'D6'): 450.21,
    ('S2', 'D1'): 22.53, ('S2', 'D1_Extra'): 22.53, ('S2', 'D2'): 32.91, ('S2', 'D2_Extra'): 32.91,
    ('S2', 'D3'): 16.47, ('S2', 'D3_Extra'): 16.47, ('S2', 'D4'): 0.88, ('S2', 'D4_Extra'): 0.88,
    ('S2', 'D5'): 32.59, ('S2', 'D5_Extra'): 32.59, ('S2', 'D6'): 362.23,
    ('S3', 'D1'): 89.86, ('S3', 'D1_Extra'): 89.86, ('S3', 'D2'): 136.63, ('S3', 'D2_Extra'): 136.63,
    ('S3', 'D3'): 36.72, ('S3', 'D3_Extra'): 36.72, ('S3', 'D4'): M, ('S3', 'D4_Extra'): M,
    ('S3', 'D5'): 26.43, ('S3', 'D5_Extra'): 26.43, ('S3', 'D6'): 1430.93,
    ('S4', 'D1'): 35.4, ('S4', 'D1_Extra'): 35.4, ('S4', 'D2'): 25.86, ('S4', 'D2_Extra'): 25.86,
    ('S4', 'D3'): 8.43, ('S4', 'D3_Extra'): 8.43, ('S4', 'D4'): 11.74, ('S4', 'D4_Extra'): 11.74,
    ('S4', 'D5'): 19.89, ('S4', 'D5_Extra'): 19.89, ('S4', 'D6'): 1306.72,
    ('S5', 'D1'): 48.76, ('S5', 'D1_Extra'): 48.76, ('S5', 'D2'): 36.94, ('S5', 'D2_Extra'): 36.94,
    ('S5', 'D3'): 114.79, ('S5', 'D3_Extra'): 114.79, ('S5', 'D4'): 16.04, ('S5', 'D4_Extra'): 16.04,
    ('S5', 'D5'): 26.35, ('S5', 'D5_Extra'): 26.35, ('S5', 'D6'): 2477.75,
    ('S6_Dummy', 'D1'): M, ('S6_Dummy', 'D1_Extra'): 0, ('S6_Dummy', 'D2'): M, ('S6_Dummy', 'D2_Extra'): 0,
    ('S6_Dummy', 'D3'): M, ('S6_Dummy', 'D3_Extra'): 0, ('S6_Dummy', 'D4'): M, ('S6_Dummy', 'D4_Extra'): 0,
    ('S6_Dummy', 'D5'): M, ('S6_Dummy', 'D5_Extra'): 0, ('S6_Dummy', 'D6'): M
}

# Supply and demand (scaled down by 1e6)
scale_factor = 1e6
supply = {
    'S1': 612.297460, 'S2': 2051.686417, 'S3': 5.255930, 'S4': 46.861157, 'S5': 3.821105, 'S6_Dummy': 1029.901800
}
demand = {
    'D1': 184.864425, 'D1_Extra': 79.227610, 'D2': 598.789581, 'D2_Extra': 322.425161, 'D3': 0.300077,
    'D3_Extra': 0.033342, 'D4': 140.119184, 'D4_Extra': 12.184277, 'D5': 1680.755288, 'D5_Extra': 720.323695,
    'D6': 10.801229
}

# Create the LP problem
prob = LpProblem("Transportation_Problem", LpMinimize)

# Define decision variables
x = LpVariable.dicts("ship", [(s, d) for s in sources for d in destinations], lowBound=0, cat='Continuous')

# Objective function: Minimize total cost
prob += lpSum(costs[(s, d)] * x[(s, d)] for s in sources for d in destinations), "Total_Cost"

# Supply constraints
for s in sources:
    prob += lpSum(x[(s, d)] for d in destinations) == supply[s], f"Supply_{s}"

# Demand constraints
for d in destinations:
    prob += lpSum(x[(s, d)] for s in sources) == demand[d], f"Demand_{d}"

# Solve the problem with CBC solver options
prob.solve(PULP_CBC_CMD(msg=1, timeLimit=3600, gapRel=0.001))

# Check solver status
print(f"Status: {LpStatus[prob.status]}")
if LpStatus[prob.status] == 'Optimal':
    print("Optimal solution found.")
    print(f"Minimum transportation cost (scaled): {value(prob.objective):.2f}")
    print(f"Minimum transportation cost (original): {value(prob.objective) * scale_factor:.2f}\n")
    
    # Create allocation table (scaled values)
    allocation = pd.DataFrame(0.0, index=sources, columns=destinations)
    for s in sources:
        for d in destinations:
            allocation.loc[s, d] = value(x[(s, d)])
    
    print("Allocation Table (scaled by 1e6):")
    print(allocation)
    
    # Scale back allocations for display
    allocation_original = allocation * scale_factor
    print("\nAllocation Table (original values):")
    print(allocation_original)
else:
    print(f"No optimal solution found. Solver status: {LpStatus[prob.status]}")
    if LpStatus[prob.status] == 'Infeasible':
        print("The problem is infeasible. Check constraints or data for inconsistencies.")
        print("Consider further reducing Big M or increasing scale factor.")
    elif LpStatus[prob.status] == 'Unbounded':
        print("The problem is unbounded. Check cost coefficients or constraints.")
    else:
        print("Other solver issue. Consider adjusting solver parameters or checking model setup.")