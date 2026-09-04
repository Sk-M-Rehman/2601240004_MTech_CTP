# ==========================================
#       LIBRARY BOOK SEARCH SYSTEM
#       USING BINARY SEARCH
# ==========================================

books = []


# ------------------------------------------
# Take number of books at runtime
# ------------------------------------------

n = int(input("Enter total number of books: "))


# ------------------------------------------
# Create sorted book numbers
# ------------------------------------------

for book_no in range(1, n + 1):
    books.append(book_no)


# ------------------------------------------
# Take book number to search
# ------------------------------------------

book_no = int(input("Enter the book number to search: "))


# ------------------------------------------
# Binary Search
# ------------------------------------------

low = 0
high = len(books) - 1

found = False


while low <= high:

    # Find middle position
    mid = (low + high) // 2


    # Book found
    if books[mid] == book_no:

        found = True

        position = mid + 1

        break


    # Search in right half
    elif books[mid] < book_no:

        low = mid + 1


    # Search in left half
    else:

        high = mid - 1


# ------------------------------------------
# Display result
# ------------------------------------------

print("\n================================")
print("       BOOK SEARCH RESULT")
print("================================")

if found:

    print("Book found")
    print("Book Number:", book_no)
    print("Book Position:", position)

else:

    print("Book not found")
