class InsufficientBalanceError(Exception):
    pass
balance=1000
withdraw=1500
try:
    if withdraw > balance:
        raise InsufficientBalanceError("Insufficient balance")
    balance -= withdraw

except InsufficientBalanceError as e:
    print(e)


age = int(input("Enter your age: "))
if age < 18:
    raise ValueError("Age must be 18 or above.")
print("You are eligible.")
    