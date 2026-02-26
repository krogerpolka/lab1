#1
import math

a = int(input("Input degree: "))
pi= 3.142848
radian = a*pi/180
print("Output radian:", round(radian, 6))

#2
import math

h = int(input("Height:"))
sb = int(input("Base, first value:"))
bb = int(input("Base, second value:"))

print("Expected output(AREA ):", (sb+bb)*h/2)

#3
import math

a = int(input("Input number of sides:"))
b = int(input("Input the length of a side:"))
c = b/(2 * math.tan(math.pi/a))

print("The area of the polygon is:", a*b*c/2)

#4
import math

a = float(input("Length of base: "))
b = float(input("Height of parallelogram: "))

print("Expected Output(AREA):", a * b)