x = int(input())
y = int(input())
z = lambda x, y: x * y #small anonymous function. Any number of arguments, but can only have one expression.
print(z(x, y))  