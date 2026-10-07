comparisons = 0
merge_operations = 0


def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2

    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


def merge(left, right):
    global comparisons, merge_operations

    merge_operations += 1

    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        comparisons += 1

        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result


arr = list(map(int, input("Enter salaries: ").split()))
print("original:",arr)
sorted_arr=merge_sort(arr)
print("sorted salaries:",sorted_arr)
print("comparisons:",comparisons)
