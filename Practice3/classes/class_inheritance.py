class Person:
    
    def __init__(self, fname, lname):
        self.firstname = fname  
        self.lastname = lname    

    def printname(self):
        print(self.firstname, self.lastname)


class Student(Person):
    # The Student class inherits from the Person class

    def __init__(self, fname, lname, year): #stops to inherit __init__ of Person

        #inherit from Person 2 arguments
        super().__init__(fname, lname)

        # Add an extra 
        self.graduationyear = year

    def welcome(self):
        # This method prints a welcome message for the student
        print("Welcome", self.firstname, self.lastname, 
              "to the class of", self.graduationyear)
x = Student("Mike", "Olsen", 2024)
x.welcome()
