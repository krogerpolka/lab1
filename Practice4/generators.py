#1
def square(num):
    for i in range(num+1):
        yield i*i

a = int(input())
print(*square(a)) #unpack all values

#2
def even(num):
    for i in range(num+1):
        if i%2 == 0:
            yield i

a = int(input())
print(*even(a), sep=',')

#3
def div(num):
    for i in range(num+1):
        if i%3 == 0 and i%4 == 0:
            yield i

a = int(input())
print(*div(a))

#4
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

a = int(input())
b = int(input())

for value in squares(a, b): #another way to see result without *
    print(value)

#5
def down(a):
    while a>=0:
        yield a
        a -= 1
        

a = int(input())
print(*down(a))

