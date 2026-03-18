from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map applies a function to each element
squared = list(map(lambda x: x**2, numbers))
print("Squared numbers:", squared)

# filter keeps elements that satisfy condition
even = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", even)

# reduce combines all elements into one value
sum_numbers = reduce(lambda x, y: x + y, numbers)
print("Sum:", sum_numbers)