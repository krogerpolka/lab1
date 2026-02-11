# Base class
class me:
    def __init__(self, fname, lname):
        self.firstname = fname   # Save first name
        self.lastname = lname    # Save last name

    # Method to print full name
    def printname(self):
        print(self.firstname, self.lastname)


# Child class (inherits from me)
class Student(me):
    def __init__(self, fname, lname):
        super().__init__(fname, lname)  # Call parent constructor
        self.graduationyear = 2025     # Add new attribute

    # Method overriding: change behavior of printname
    def printname(self):
        print(self.firstname, self.lastname, "- Student")  # Add extra info


# Create object of Student
x = Student("Nurassyl", "Nazyrbek")

# Call overridden method
x.printname()  # Prints: Nurassyl Nazyrbek - Student

# Access additional attribute
print(x.graduationyear)  # Prints: 2026
