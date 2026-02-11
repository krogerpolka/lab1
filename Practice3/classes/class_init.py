class Game:
  def __init__(self, name, age, founder):
    self.name = name
    self.age = age
    self.founder = founder
    

g1 = Game("Linus", 30, "Osmalo")
g2= Game("CS2", 50, "Son Hiyang")

print(g1.name)
print(g1.age)
print(g1.founder)
