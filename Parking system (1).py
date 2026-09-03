from datetime import datetime
import math

# Total number of parking slots
total_slots = 100

# Store information about all parking slots
parking_slots = {}

# Create 100 parking slots
for slot in range(1, total_slots + 1):
    parking_slots[slot] = {
        "status": "Available",
        "vehicle_number": None,
        "vehicle_type": None,
        "entry_time": None,
        "exit_time": None,
        "charge": 0
    }

# Vehicle parking rates per hour
rates = {
    "Car": 30,
    "Bike": 10,
    "Truck": 50,
    "Bus": 60
}

while True:

    print("\n================================")
    print("     PARKING MANAGEMENT SYSTEM")
    print("================================")
    print("1. Display Available Slots")
    print("2. Allocate Slot")
    print("3. Release Slot")
    print("4. Display All Slot Information")
    print("5. Display Occupied Slots")
    print("6. Check Parking Full")
    print("7. Exit")
    print("================================")

    choice = input("Enter your choice: ")

    # --------------------------------
    # 1. Display available slots
    # --------------------------------
    if choice == "1":

        available_slots = []

        for slot in parking_slots:
            if parking_slots[slot]["status"] == "Available":
                available_slots.append(slot)

        print("\nAvailable Parking Slots:")
        print(available_slots)
        print("Total Available Slots:", len(available_slots))

    # --------------------------------
    # 2. Allocate a parking slot
    # --------------------------------
    elif choice == "2":

        vehicle_number = input("Enter vehicle number: ")
        vehicle_type = input("Enter vehicle type (Car/Bike/Truck/Bus): ").capitalize()

        if vehicle_type not in rates:
            print("Invalid vehicle type!")

        else:

            # Check if vehicle is already parked
            already_parked = False

            for slot in parking_slots:
                if parking_slots[slot]["vehicle_number"] == vehicle_number:
                    already_parked = True
                    print("Vehicle is already parked in slot", slot)
                    break

            if already_parked:
                continue

            # Find an available slot
            allocated = False

            for slot in parking_slots:

                if parking_slots[slot]["status"] == "Available":

                    parking_slots[slot]["status"] = "Occupied"
                    parking_slots[slot]["vehicle_number"] = vehicle_number
                    parking_slots[slot]["vehicle_type"] = vehicle_type
                    parking_slots[slot]["entry_time"] = datetime.now()
                    parking_slots[slot]["exit_time"] = None
                    parking_slots[slot]["charge"] = 0

                    print("\nVehicle successfully parked!")
                    print("Vehicle Number:", vehicle_number)
                    print("Vehicle Type:", vehicle_type)
                    print("Allocated Slot:", slot)
                    print(
                        "Entry Time:",
                        parking_slots[slot]["entry_time"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )

                    allocated = True
                    break

            if not allocated:
                print("Parking is FULL!")

    # --------------------------------
    # 3. Release a parking slot
    # --------------------------------
    elif choice == "3":

        vehicle_number = input("Enter vehicle number: ")

        vehicle_found = False

        for slot in parking_slots:

            if parking_slots[slot]["vehicle_number"] == vehicle_number:

                vehicle_found = True

                # Store exit time
                exit_time = datetime.now()
                parking_slots[slot]["exit_time"] = exit_time

                # Calculate parking duration
                entry_time = parking_slots[slot]["entry_time"]

                duration = exit_time - entry_time

                hours = duration.total_seconds() / 3600

                # Round up to next hour
                charged_hours = max(1, math.ceil(hours))

                # Get vehicle type and rate
                vehicle_type = parking_slots[slot]["vehicle_type"]
                rate = rates[vehicle_type]

                # Calculate charge
                charge = charged_hours * rate

                parking_slots[slot]["charge"] = charge

                print("\n========== PARKING BILL ==========")
                print("Vehicle Number:", vehicle_number)
                print("Vehicle Type:", vehicle_type)
                print("Parking Slot:", slot)
                print(
                    "Entry Time:",
                    entry_time.strftime("%Y-%m-%d %H:%M:%S")
                )
                print(
                    "Exit Time:",
                    exit_time.strftime("%Y-%m-%d %H:%M:%S")
                )
                print("Parking Duration: %.2f hours" % hours)
                print("Charged Hours:", charged_hours)
                print("Rate per Hour: ₹", rate)
                print("Total Parking Charge: ₹", charge)
                print("=================================")

                # Make slot available again
                parking_slots[slot]["status"] = "Available"
                parking_slots[slot]["vehicle_number"] = None
                parking_slots[slot]["vehicle_type"] = None
                parking_slots[slot]["entry_time"] = None
                parking_slots[slot]["exit_time"] = None

                break

        if not vehicle_found:
            print("Vehicle not found!")

    # --------------------------------
    # 4. Display all slot information
    # --------------------------------
    elif choice == "4":

        print("\n========== ALL PARKING SLOTS ==========")

        for slot in parking_slots:

            print(
                "Slot:", slot,
                "| Status:", parking_slots[slot]["status"],
                "| Vehicle:", parking_slots[slot]["vehicle_number"],
                "| Type:", parking_slots[slot]["vehicle_type"]
            )

    # --------------------------------
    # 5. Display occupied slots
    # --------------------------------
    elif choice == "5":

        print("\n========== OCCUPIED SLOTS ==========")

        found = False

        for slot in parking_slots:

            if parking_slots[slot]["status"] == "Occupied":

                found = True

                print(
                    "Slot:", slot,
                    "| Vehicle:", parking_slots[slot]["vehicle_number"],
                    "| Type:", parking_slots[slot]["vehicle_type"],
                    "| Entry Time:",
                    parking_slots[slot]["entry_time"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

        if not found:
            print("No vehicles are currently parked.")

    # --------------------------------
    # 6. Check whether parking is full
    # --------------------------------
    elif choice == "6":

        occupied = 0

        for slot in parking_slots:

            if parking_slots[slot]["status"] == "Occupied":
                occupied += 1

        available = total_slots - occupied

        print("\n========== PARKING STATUS ==========")
        print("Total Slots:", total_slots)
        print("Occupied Slots:", occupied)
        print("Available Slots:", available)

        if occupied == total_slots:
            print("Parking is FULL!")
        else:
            print("Parking is NOT FULL.")

    # --------------------------------
    # 7. Exit
    # --------------------------------
    elif choice == "7":

        print("Thank you for using the Parking Management System!")
        break

    else:
        print("Invalid choice! Please enter a number from 1 to 7.")