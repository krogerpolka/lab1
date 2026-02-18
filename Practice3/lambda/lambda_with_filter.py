numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
even_numbers = list(filter(lambda x: x % 2 == 0, numbers)) #creates a list of items for which a function returns True
print(even_numbers)