import cal

print(cal.add(10,20))
print(cal.multiply(5,4))

#2 import functions from cal.py
from cal import add

print(add(10,20))

#3 import multiple functions from cal.py
from cal import add,multiply

print(add(10,20))
print(multiply(5,4))

#4 import all functions from cal.py
from cal import *