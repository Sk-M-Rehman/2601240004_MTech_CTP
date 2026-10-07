1. What is Merge Sort?

Answer:
Merge Sort is a divide-and-conquer sorting algorithm that divides an array into smaller parts, sorts them, and merges them.
It repeatedly divides the array into two halves until each part contains only one element.
Then, it merges these smaller parts in sorted order.
The time complexity of Merge Sort is O(n log n).
It works efficiently even for large datasets.

2. What is the purpose of the merge() function?

Answer:
The merge() function combines two already sorted arrays into one sorted array.
It compares the first available elements of both arrays.
The smaller element is added to the result.
This process continues until one of the arrays becomes empty.
Finally, the remaining elements are added to the result array.

3. What does mid = len(arr) // 2 do?

Answer:
It finds the middle position to divide the array into two halves.
len(arr) gives the total number of elements in the array.
The // operator performs integer division.
The left half is taken using arr[:mid], and the right half using arr[mid:].
This division is repeated recursively until the arrays contain one or zero elements.

4. Why isn't Merge Sort O(n²)?

Answer:
Merge Sort is not O(n²) because the array is divided into halves at every step, reducing the problem size exponentially.
There are approximately log₂ n levels of division.
At each level, merging all the elements takes O(n) time.
Therefore, the total complexity is O(n log n).
This makes Merge Sort more efficient than algorithms such as Bubble Sort for large inputs.

5. Does Merge Sort modify the original array directly?

Answer:
In this program, no. It creates new lists using slicing and merging.
The expressions arr[:mid] and arr[mid:] create separate lists for the left and right halves.
The merge() function also creates a new result list.
Finally, the sorted list is returned by the merge_sort() function.
Therefore, the original input list is not modified directly in this implementation.
