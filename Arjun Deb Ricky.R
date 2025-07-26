# Load required package
library(lpSolve)

# Define the cost matrix (6 sources x 11 destinations)
# Sources: S1, S2, S3, S4, S5, S6 (Dummy)
# Destinations: D1, D1(Extra), D2, D2(Extra), D3, D3(Extra), D4, D4(Extra), D5, D5(Extra), D6
# M is a large penalty (e.g., 1e9)
M <- 1e9
cost_matrix <- matrix(c(
  22.8, 22.8, 56.18, 56.18, 13.19, 13.19, 4.6, 4.6, 28.31, 28.31, 450.21,        # S1
  22.53, 22.53, 32.91, 32.91, 16.47, 16.47, 0.88, 0.88, 32.59, 32.59, 362.23,    # S2
  89.86, 89.86, 136.63, 136.63, 36.72, 36.72, M, M, 26.43, 26.43, 1430.93,       # S3
  35.4, 35.4, 25.86, 25.86, 8.43, 8.43, 11.74, 11.74, 19.89, 19.89, 1306.72,     # S4
  48.76, 48.76, 36.94, 36.94, 114.79, 114.79, 16.04, 16.04, 26.35, 26.35, 2477.75, # S5
  M, 0, M, 0, M, 0, M, 0, M, 0, M                                                  # S6 (Dummy)
), nrow = 6, byrow = TRUE)

# Define supply and demand
supply <- c(612297460, 2051686417, 5255930, 46861157, 3821105, 1029901800)
demand <- c(184864425, 79227610, 598789581, 322425161, 300077, 33342, 140119184, 12184277, 1680755288, 720323695, 10801229)

# Verify that total supply equals total demand
sum(supply)  # 3749823869
sum(demand)  # 3749823869 (balanced for minimum demand)

# Set up the linear programming problem
# Number of variables: 6 sources * 11 destinations = 66
f.obj <- as.vector(t(cost_matrix))  # Objective function coefficients (flattened cost matrix)

# Constraints
# 1. Supply constraints (6 rows)
# 2. Demand constraints (11 columns)
f.con <- matrix(0, nrow = 6 + 11, ncol = 66)
f.dir <- c(rep("=", 6), rep("=", 11))
f.rhs <- c(supply, demand)

# Supply constraints: sum of allocations from each source equals its supply
for (i in 1:6) {
  f.con[i, ((i-1)*11 + 1):(i*11)] <- 1
}

# Demand constraints: sum of allocations to each destination equals its demand
for (j in 1:11) {
  f.con[6 + j, seq(j, 66, by = 11)] <- 1
}

# Solve the linear programming problem
lp_solution <- lp("min", f.obj, f.con, f.dir, f.rhs)

# Check if solution was successful
if (lp_solution$status == 0) {
  cat("Optimal solution found.\n")
  cat("Minimum transportation cost:", lp_solution$objval, "\n\n")
  
  # Reshape solution into 6x11 matrix for allocation table
  allocation <- matrix(lp_solution$solution, nrow = 6, byrow = TRUE)
  colnames(allocation) <- c("D1", "D1_Extra", "D2", "D2_Extra", "D3", "D3_Extra", "D4", "D4_Extra", "D5", "D5_Extra", "D6")
  rownames(allocation) <- c("S1", "S2", "S3", "S4", "S5", "S6_Dummy")
  
  # Print allocation table
  cat("Allocation Table:\n")
  print(allocation)
} else {
  cat("No optimal solution found.\n")
}