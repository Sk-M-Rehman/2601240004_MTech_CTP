# ==========================================
#       ATM LOCATION MANAGEMENT SYSTEM
#       USING BRUTE FORCE ALGORITHM
# ==========================================

import math

points = []


# ------------------------------------------
# Take number of ATMs from user
# ------------------------------------------

n = int(input("Enter number of ATMs: "))


# ------------------------------------------
# Take ATM details at runtime
# ------------------------------------------

for i in range(n):

    print("\nEnter details for ATM", i + 1)

    name = input("Enter ATM name: ")
    x = float(input("Enter X coordinate: "))
    y = float(input("Enter Y coordinate: "))

    points.append((name, x, y))


# ------------------------------------------
# Find closest pair of ATMs
# ------------------------------------------

minimum_distance = float("inf")

closest_atm1 = ""
closest_atm2 = ""


# Compare every pair of ATMs
for i in range(len(points)):

    for j in range(i + 1, len(points)):

        x1 = points[i][1]
        y1 = points[i][2]

        x2 = points[j][1]
        y2 = points[j][2]


        # Calculate Euclidean distance
        distance = math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        )


        # Check for minimum distance
        if distance < minimum_distance:

            minimum_distance = distance

            closest_atm1 = points[i][0]
            closest_atm2 = points[j][0]


# ------------------------------------------
# Display ATM locations
# ------------------------------------------

print("\n==============================================")
print("              ATM LOCATIONS")
print("==============================================")
print()

for name, x, y in points:

    print(
        name,
        ": (",
        x,
        ",",
        y,
        ")"
    )


# ------------------------------------------
# Display closest pair
# ------------------------------------------

print("\n==============================================")
print("             CLOSEST ATM PAIR")
print("==============================================")

print(
    "Closest ATMs:",
    closest_atm1,
    "and",
    closest_atm2
)

print(
    "Distance:",
    round(minimum_distance, 2)
)
