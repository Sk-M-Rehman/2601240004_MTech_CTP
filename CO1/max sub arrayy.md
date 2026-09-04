The Maximum Profit Analysis System is a Python-based application that allows users to enter the daily profit or loss of a business and identify the continuous sequence of days that generates the maximum total profit. The program uses a runtime input system, where the user can enter the number of days and the profit or loss for each day.

The system stores the daily profit and loss values in a Python list. Positive values represent profits, while negative values represent losses.

Main Features

Enter Number of Days: Users can enter the total number of business days at runtime.

Enter Daily Profit/Loss: Users can provide the profit or loss for each day.

Store Daily Data: All profit and loss values are stored in a Python list.

Find Maximum Profit: The program uses Kadane's Algorithm to find the continuous sequence of days with the maximum total profit.

Track Starting and Ending Days: The program keeps track of the beginning and ending days of the maximum-profit sequence.

Display Daily Profit/Loss: The program displays the profit or loss recorded for every day.

Display Maximum Profit: The program displays the maximum total profit obtained from a continuous sequence of days.

Display Days Included: The program displays all the days that contributed to the maximum profit.

Algorithm

The program uses Kadane's Algorithm, a dynamic programming-based algorithm used to find the maximum sum subarray.

For every day's profit or loss, the program decides whether to:

Start a new sequence from the current day, or
Continue the existing sequence.

The algorithm maintains two values:

Current Sum: Maximum profit ending at the current day.

Maximum Sum: Maximum profit found so far.

This allows the program to find the maximum continuous profit sequence efficiently without checking every possible combination of days.

This project demonstrates important Python concepts such as lists, loops, conditional statements, user input, variables, indexing, and Kadane's Algorithm. It can be used as a basic model for developing a real-world business profit analysis and financial performance management system.
