# Define a class
class me:
  
  # Constructor (runs when object is created)
  def __init__(self, fname, lname):
    self.firstname = fname   # Save first name
    self.lastname = lname    # Save last name

  # Method to print full name
  def printname(self):
    print(self.firstname, self.lastname)


# Create object of the class
x = me("Nurassyl", "Nazyrbek")

# Call the method
x.printname()
