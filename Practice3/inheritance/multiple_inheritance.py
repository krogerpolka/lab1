# First base class
class me:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


# Second base class
class Info:
    def __init__(self, age):
        self.age = age

    def printage(self):
        print("Age:", self.age)


# Child class with multiple inheritance
class Student(me, Info):
    def __init__(self, fname, lname, age, graduationyear):
        me.__init__(self, fname, lname)       # Initialize me part
        Info.__init__(self, age)               # Initialize Info part
        self.graduationyear = graduationyear  # Add new attribute

    # Overriding printname method
    def printname(self):
        print(self.firstname, self.lastname, "- Student")


# Create object of Student
x = Student("Nurassyl", "Nazyrbek", 20, 2026)

# Call methods
x.printname()       # Prints: Nurassyl Nazyrbek - Student
x.printage()        # Prints: Age: 20
print(x.graduationyear)  # Prints: 2026
