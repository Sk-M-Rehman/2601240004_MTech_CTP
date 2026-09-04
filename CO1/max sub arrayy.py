# ==========================================
#       MAXIMUM PROFIT ANALYSIS SYSTEM
#       USING KADANE'S ALGORITHM
# ==========================================

profits = []


# ------------------------------------------
# Take number of days at runtime
# ------------------------------------------

n = int(input("Enter number of days: "))


# ------------------------------------------
# Take daily profit/loss at runtime
# ------------------------------------------

for i in range(n):

    profit = float(
        input("Enter profit/loss for Day " + str(i + 1) + ": ")
    )

    profits.append(profit)


# ------------------------------------------
# Kadane's Algorithm
# ------------------------------------------

current_sum = profits[0]
maximum_sum = profits[0]

start = 0
end = 0
temp_start = 0


for i in range(1, len(profits)):

    # Decide whether to start a new sequence
    # or continue the existing sequence

    if profits[i] > current_sum + profits[i]:

        current_sum = profits[i]

        temp_start = i

    else:

        current_sum = current_sum + profits[i]


    # Update maximum profit
    if current_sum > maximum_sum:

        maximum_sum = current_sum

        start = temp_start
        end = i


# ------------------------------------------
# Display daily profit/loss
# ------------------------------------------

print("\n==============================================")
print("          DAILY PROFIT / LOSS")
print("==============================================")

for i in range(len(profits)):

    print(
        "Day", i + 1,
        ":",
        profits[i]
    )


# ------------------------------------------
# Display maximum profit
# ------------------------------------------

print("\n==============================================")
print("             MAXIMUM PROFIT")
print("==============================================")

print("Maximum Profit:", maximum_sum)


# ------------------------------------------
# Display days included
# ------------------------------------------

print("\n==============================================")
print("             DAYS INCLUDED")
print("==============================================")

for i in range(start, end + 1):

    print(
        "Day", i + 1,
        ":",
        profits[i]
    )
