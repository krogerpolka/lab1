def my_function(*names):
  total = 0
  for x in names: # How many names here
    total += 1
  return total

print(my_function("Julie", "Mike", "Cock"))
print(my_function("Ulka", "Molai"))
