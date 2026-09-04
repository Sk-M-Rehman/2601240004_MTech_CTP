# Student Attendance Management System

students = []

# Get number of students
n = int(input("Enter number of students: "))

# -----------------------------------------
# Taking student details
# -----------------------------------------

for i in range(n):

    print("\nEnter details for Student", i + 1)

    student_id = input("Enter Student ID: ")
    name = input("Enter Student Name: ")

    total_classes = int(input("Enter Total Classes Conducted: "))
    attended_classes = int(input("Enter Total Classes Attended: "))

    # Calculate attendance percentage
    attendance_percentage = (
        attended_classes / total_classes
    ) * 100

    # Store student information
    student = {
        "id": student_id,
        "name": name,
        "total_classes": total_classes,
        "attended_classes": attended_classes,
        "attendance_percentage": attendance_percentage
    }

    students.append(student)


# -----------------------------------------
# Display attendance of all students
# -----------------------------------------

print("\n==============================================")
print("        STUDENT ATTENDANCE DETAILS")
print("==============================================")

for student in students:

    print("Student ID:", student["id"])
    print("Name:", student["name"])
    print("Total Classes:", student["total_classes"])
    print("Classes Attended:", student["attended_classes"])
    print(
        "Attendance Percentage:",
        round(student["attendance_percentage"], 2),
        "%"
    )
    print("----------------------------------------------")


# -----------------------------------------
# Students having attendance below 75%
# -----------------------------------------

print("\n==============================================")
print("       STUDENTS BELOW 75% ATTENDANCE")
print("==============================================")

below_75 = []

for student in students:

    if student["attendance_percentage"] < 75:
        below_75.append(student)

if len(below_75) == 0:

    print("No student has attendance below 75%.")

else:

    for student in below_75:

        print(
            "ID:", student["id"],
            "| Name:", student["name"],
            "| Attendance:",
            round(student["attendance_percentage"], 2),
            "%"
        )


# -----------------------------------------
# Find student with highest attendance
# -----------------------------------------

highest_attendance = students[0]

for student in students:

    if (
        student["attendance_percentage"]
        > highest_attendance["attendance_percentage"]
    ):
        highest_attendance = student


print("\n==============================================")
print("        HIGHEST ATTENDANCE")
print("==============================================")

print("Student ID:", highest_attendance["id"])
print("Name:", highest_attendance["name"])
print(
    "Attendance:",
    round(highest_attendance["attendance_percentage"], 2),
    "%"
)


# -----------------------------------------
# Calculate whole class average attendance
# -----------------------------------------

total_attendance_percentage = 0

for student in students:

    total_attendance_percentage += student["attendance_percentage"]

class_average = total_attendance_percentage / len(students)


print("\n==============================================")
print("        WHOLE CLASS AVERAGE")
print("==============================================")

print(
    "Class Average Attendance:",
    round(class_average, 2),
    "%"
)
