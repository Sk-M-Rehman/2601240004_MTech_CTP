The Library Book Search System is a Python-based application that allows users to search for a particular book from a large collection of books using the Binary Search algorithm. The program takes the total number of books and the book number to be searched as runtime inputs.

The system stores the book numbers in a sorted Python list, where each book is represented by a unique number starting from 1.

Main Features

Enter Number of Books: Users can enter the total number of books available in the library at runtime.

Create Book Database: The program creates a sorted list of book numbers from 1 to the specified number of books.

Search Book: Users can enter the book number they want to search for.

Binary Search: The program uses Binary Search to efficiently locate the required book.

Display Search Result: If the book is found, the program displays the book number and its position in the library list. Otherwise, it displays a book-not-found message.

Algorithm

The program uses the Binary Search algorithm, which works only on sorted data. Instead of checking every book one by one, the algorithm repeatedly checks the middle book and eliminates half of the remaining search area.

For example, when searching for Book 75000 among 1,000,000 books, the program initially checks the middle position. Since 75000 is smaller than the middle value, it searches only the left half. This process continues until Book 75000 is found.

If search book > middle book: Search the right half.

If search book < middle book: Search the left half.

If search book = middle book: Book is found.

This project demonstrates important Python concepts such as lists, loops, conditional statements, user input, indexing, and the Binary Search algorithm. It can be used as a basic model for developing a real-world library book searching and inventory management system.
