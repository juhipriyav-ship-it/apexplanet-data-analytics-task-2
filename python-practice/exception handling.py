'''try:
    number = int(input("Enter number: "))
    result = 100 / number
    print(result)

except ZeroDivisionError:
    print("Cannot divide by zero")'''

'''#2 handling multiple exceptions
try:
    number=int(input("Enter number: "))
    print(100 / number)
except ValueError:
    print("Please enter a number")

except ZeroDivisionError:
    print("Cannot divide by zero")'''

#3 using else and finally
try:
    number=int(input("Enter number: "))
    print(100 / number)
except ValueError:
    print("Please enter a number")

except ZeroDivisionError:
    print("Cannot divide by zero")

else:
    print("No exceptions occurred")

finally:
    print("This will always execute")

