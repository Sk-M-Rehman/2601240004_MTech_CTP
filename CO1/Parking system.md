The Parking Management System is a Python-based application designed to manage vehicle parking in a parking area with 100 parking slots. It uses a menu-driven interface that allows users to perform different parking operations, such as checking available slots, allocating slots to vehicles, releasing vehicles, and calculating parking charges.

Each parking slot is stored using a dictionary, which contains information such as:

Slot status
Vehicle number
Vehicle type
Entry time
Exit time
Parking charge

The system supports different vehicle types, including Car, Bike, Truck, and Bus, with different parking rates per hour.

Main Features
Display Available Slots: Shows all currently available parking slots and their total count.
Allocate Slot: Automatically assigns the first available slot to a vehicle and records its entry time.
Vehicle Validation: Checks whether the vehicle type is valid and prevents the same vehicle from being parked multiple times.
Release Slot: Removes a vehicle from its parking slot and generates a parking bill.
Parking Charge Calculation: Calculates the parking duration and charges the vehicle based on its type and hourly rate.
Round-Up Hourly Billing: Even if a vehicle is parked for a fraction of an hour, the parking time is rounded up to the next hour, with a minimum charge of one hour.
Display All Slot Information: Shows the status and vehicle details of all 100 parking slots.
Display Occupied Slots: Displays details of all vehicles currently parked.
Check Parking Status: Shows the total number of slots, occupied slots, and available slots, and checks whether the parking area is full.
Exit: Terminates the program safely.
Parking Charge Formula

Parking Duration = Exit Time − Entry Time

Charged Hours = Rounded-up Parking Duration

Parking Charge = Charged Hours × Rate per Hour

This project demonstrates important Python concepts such as dictionaries, loops, conditional statements, user input, date and time handling using datetime, mathematical calculations using math, and menu-driven programming. It provides a basic implementation of a real-world vehicle parking and billing management system.
