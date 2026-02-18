#Arbitrary Arguments
def my_function(*names):#if we do not know how many variables
  total = 0
  for x in names: # How many names here
    total += 1
  return total

print(my_function("Julie", "Mike", "Cock"))
print(my_function("Ulka", "Molai"))

#Arbitrary Keyword Arguments
def my_function(**me): #allows a function to accept any number of keyword arguments.
  print("My name is" + me["name"])

my_function(name = "Nurassyl", surname = "Nazyrbek")