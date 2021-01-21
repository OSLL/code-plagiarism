def binary_search(my_list, item):
    low = 0
    hight = len(my_list) - 1

    while low <= hight:
        mid = (low + hight) // 2
        guess = my_list[mid]
        if guess == item:
            return mid
        if guess > item:
            hight = mid - 1
        else:
            low = mid + 1
    return None

my_list = [1, 3, 5, 7 , 9]

print(binary_search(my_list, 3))
print(binary_search(my_list, 7))
