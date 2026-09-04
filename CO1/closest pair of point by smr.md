The ATM Location Management System is a Python-based application that allows users to enter the locations of multiple ATMs and find the two ATMs that are closest to each other. The program uses a runtime input system, where the user can enter the number of ATMs along with their names and coordinates.

The system stores ATM information using tuples inside a Python list. Each ATM record contains the ATM name, X-coordinate, and Y-coordinate.

Main Features

Enter ATM Details: Users can enter the number of ATMs and provide each ATM's name and coordinates at runtime.

Store ATM Information: ATM names and coordinates are stored as tuples inside a Python list.

Calculate Distance: The program calculates the distance between every pair of ATMs using the Euclidean distance formula.

Find Closest Pair: The program compares all possible pairs and identifies the two ATMs having the minimum distance.

Display ATM Locations: The program displays the names and coordinates of all entered ATMs.

Display Closest ATMs: The program displays the two closest ATMs along with the calculated distance between them.

Calculation Formula

The program uses the Euclidean Distance Formula:

Distance = √((x₂ − x₁)² + (y₂ − y₁)²)

For example, if:

ATM1 = (2, 3)
ATM2 = (4, 6)

Then:

Distance = √((4 − 2)² + (6 − 3)²)
         = √(4 + 9)
         = √13
         ≈ 3.61
Algorithm

The program uses the Brute Force algorithm to find the closest pair of ATMs. It compares every possible pair of ATM locations and calculates the distance between them. Whenever a smaller distance is found, that pair is stored as the current closest pair.

This approach is simple and suitable for a small or moderate number of ATM locations.

This project demonstrates important Python concepts such as lists, tuples, nested loops, conditional statements, user input, mathematical calculations, Euclidean distance, and the Brute Force algorithm. It can be used as a basic model for developing a real-world ATM location planning and geographic proximity management system.
