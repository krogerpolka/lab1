# Base class
class me:
  def __init__(self, fname, lname):
    self.firstname = fname   # Save first name
    self.lastname = lname    # Save last name

  def printname(self):
    print(self.firstname, self.lastname)  # Print full name


# Child class (inherits from me)
class Student(me):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)  # Call parent constructor
    self.graduationyear = 2025     # Add new attribute


# Create object of Student
x = Student("Nurassyl", "Nazyrbek")

# Print graduation year
print(x.graduationyear)
