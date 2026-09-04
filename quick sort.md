The Employee Salary Management System is a Python-based application that allows users to enter employee details, sort employees based on their salaries, and identify employees who are eligible for a salary benefit. The program uses a runtime input system, where the user can enter the number of employees along with their names and salaries.

The system stores employee details using tuples inside a Python list. Each employee record contains the employee's name and salary.

### Main Features

**Enter Employee Details:** Users can enter the number of employees and provide each employee's name and salary at runtime.

**Store Employee Information:** Employee names and salaries are stored as tuples inside a Python list.

**Sort Employees:** The program uses the **Quick Sort algorithm** to arrange employees according to their salaries.

**Descending Order:** Employees are sorted from the highest salary to the lowest salary so that the highest-paid employees appear first.

**Display Sorted Employees:** The program displays all employees along with their salaries after sorting.

**Salary Benefit Eligibility:** Employees who have a salary of **₹50,000 or above** are identified and displayed as eligible for the salary benefit.

### Algorithm

The program uses the **Quick Sort algorithm** to sort employee salaries in descending order. It selects a salary as a **pivot**, partitions the employee records based on the pivot, and repeatedly sorts the smaller sections.

This implementation uses a **stack instead of recursion**, making it an **iterative Quick Sort** implementation.

**Comparison:** Higher salaries are placed before lower salaries.

**Salary Benefit Condition:**
Salary ≥ ₹50,000 → Eligible for Salary Benefit
Salary < ₹50,000 → Not Eligible for Salary Benefit

This project demonstrates important Python concepts such as **lists, tuples, loops, conditional statements, user input, stacks, swapping, partitioning, and the Quick Sort algorithm**. It can be used as a basic model for developing a real-world **employee salary ranking and benefit management system**.
