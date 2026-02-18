class Game:
  def __init__(self, name, age, founder): # set initial values when creating the object
    self.name = name
    self.age = age
    self.founder = founder
    #Without the init, set properties for each object

g1 = Game("Linus", 30, "Osmalo")
g2= Game("CS2", 50, "Son Hiyang")

print(g1.name)
print(g1.age)
print(g1.founder)
