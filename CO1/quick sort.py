# ==========================================
#       EMPLOYEE SALARY MANAGEMENT SYSTEM
#       USING QUICK SORT
# ==========================================

employees = []

# ------------------------------------------
# Take number of employees from user
# ------------------------------------------

n = int(input("Enter number of employees: "))


# ------------------------------------------
# Take employee details at runtime
# ------------------------------------------

for i in range(n):

    print("\nEnter details for Employee", i + 1)

    name = input("Enter employee name: ")
    salary = float(input("Enter employee salary: "))

    employees.append((name, salary))


# ------------------------------------------
# Iterative Quick Sort
# ------------------------------------------

stack = [(0, len(employees) - 1)]

while stack:

    low, high = stack.pop()

    if low < high:

        # Select last element as pivot
        pivot = employees[high][1]

        i = low - 1

        # Partition the list
        for j in range(low, high):

            # Descending order
            if employees[j][1] >= pivot:

                i += 1

                employees[i], employees[j] = (
                    employees[j],
                    employees[i]
                )

        # Place pivot in correct position
        employees[i + 1], employees[high] = (
            employees[high],
            employees[i + 1]
        )

        pivot_position = i + 1

        # Add left and right portions to stack
        stack.append(
            (low, pivot_position - 1)
        )

        stack.append(
            (pivot_position + 1, high)
        )


# ------------------------------------------
# Display sorted employees
# ------------------------------------------

print("\n==============================================")
print("     EMPLOYEES SORTED BY SALARY")
print("==============================================")
print()

for name, salary in employees:

    print(name, "-", salary)


# ------------------------------------------
# Display employees eligible for benefit
# ------------------------------------------

print("\n==============================================")
print("   EMPLOYEES ELIGIBLE FOR SALARY BENEFIT")
print("==============================================")
print()

for name, salary in employees:

    if salary >= 50000:

        print(name, "-", salary)
