'''import datetime
today = datetime.date.today()
print(today)

#2 individual date components
import datetime

now = datetime.datetime.now()

print("Year:", now.year)
print("Month:", now.month)
print("Day:", now.day)
print("Hour:", now.hour)
print("Minute:", now.minute)

#3 time delta
from datetime import date,timedelta

today=date.today()
future=today+timedelta(days=7)
print(future)'''

'''import datetime
date = date.today()
print(date)'''

# %d --> day
# %m --> month
# %Y --> year
# %H --> hour
# %M --> minute
# %S --> second

# 4 formatting date and time
'''import datetime
now = datetime.datetime.now()
print(now.strftime("%d-%m-%Y"))'''

# commands

'''os.getcwd --> get current working directory
os.rename("old","new") 
os.listdir()
os.mkdir() 
os.makedirs() 
os.remove("f1")
os.path.exists() --> used in if conditions--> boolean true if it exits otherwise boolean false '''

#1 getting your current working directory
import os
print(os.getcwd())

#2 listing files and directories 
import os
print(os.listdir())

#3 creating a new directory
import os
os.mkdir("students")
if os.path.exists("students.csv"):
    print("File exists")
else:
    print("File does not exists")
os.rename("old.txt", "new.txt")
os.remove("old.txt")

#4 creating multiplr directories
import os
os.makedirs("project/data/files")

#5 adding paths
import os
path=os.path.join("data", "students.csv")
print(path)