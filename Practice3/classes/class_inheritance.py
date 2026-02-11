class Person:
    
    def __init__(self, fname, lname):
        self.firstname = fname  
        self.lastname = lname    

    def printname(self):
        print(self.firstname, self.lastname)


class Student(Person):
    # The Student class inherits from the Person class

    def __init__(self, fname, lname, year):

        # to initialize first name and last name
        super().__init__(fname, lname)

        # Add a new attribute specific to Student
        self.graduationyear = year

    def welcome(self):
        # This method prints a welcome message for the student
        print("Welcome", self.firstname, self.lastname, 
              "to the class of", self.graduationyear)
x = Student("Mike", "Olsen", 2024)
x.welcome()
