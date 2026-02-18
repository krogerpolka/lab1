names= ["John", "Mike", "Krom"] # MAP applies a function to every item in an iterable
m=list(map(lambda x: x + " " + "SUPER", names))
print(m)