The Student Scholarship Management System is a Python-based application that allows users to enter student details, sort students based on their marks, and identify students who are eligible for a scholarship. The program uses a runtime input system, where the user can enter the number of students along with their names and marks.

The system stores student details using tuples inside a Python list. Each student record contains the student's name and marks.

### Main Features

**Enter Student Details:** Users can enter the number of students and provide each student's name and marks at runtime.

**Store Student Information:** Student names and marks are stored as tuples inside a Python list.

**Sort Students:** The program uses the Merge Sort algorithm to arrange students according to their marks.

**Descending Order:** Students are sorted from the highest marks to the lowest marks so that the highest-scoring students appear first.

**Display Sorted Students:** The program displays all students along with their marks after sorting.

**Scholarship Eligibility:** Students who score 90 marks or above are identified and displayed as scholarship-eligible students.

### Algorithm

The program uses the **Merge Sort algorithm** to sort student marks in descending order. It repeatedly divides the student list into smaller parts, compares the marks of students, and merges the parts back together in sorted order.

**Comparison:** Higher marks are placed before lower marks.

**Scholarship Condition:**
Marks ≥ 90 → Eligible for Scholarship
Marks < 90 → Not Eligible for Scholarship

This project demonstrates important Python concepts such as **lists, tuples, loops, conditional statements, user input, data storage, and the Merge Sort algorithm**. It can be used as a basic model for developing a real-world **student ranking and scholarship management system**.
