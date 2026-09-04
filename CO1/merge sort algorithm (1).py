 # Take number of students from user
n = int(input("Enter number of students: "))

students = []

# Take student details at runtime
for i in range(n):
    name = input("Enter student name: ")
    marks = int(input("Enter marks: "))
    students.append((name, marks))

# Merge Sort
size = 1

while size < n:
    left = 0

    while left < n:
        mid = min(left + size, n)
        right = min(left + 2 * size, n)

        i = left
        j = mid
        temp = []

        # Merge two sorted parts
        while i < mid and j < right:
            if students[i][1] >= students[j][1]:
                temp.append(students[i])
                i += 1
            else:
                temp.append(students[j])
                j += 1

        # Add remaining elements from left part
        while i < mid:
            temp.append(students[i])
            i += 1

        # Add remaining elements from right part
        while j < right:
            temp.append(students[j])
            j += 1

        # Copy sorted elements back
        for k in range(len(temp)):
            students[left + k] = temp[k]

        left += 2 * size

    size *= 2


# Display sorted students
print("\nStudents sorted in descending order:")
print()

for name, marks in students:
    print(name, "-", marks)


# Display scholarship eligible students
print("\nStudents eligible for scholarship:")
print()

for name, marks in students:
    if marks >= 90:
        print(name, "-", marks)
