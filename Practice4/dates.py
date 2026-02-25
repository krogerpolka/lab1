#1
from datetime import date, timedelta #working with DATE and timedelta for  finding difference between dates

today  = date.today()

old_date = date - timedelta(days=5)

print(today.strftime("%m/%d/%y")) #string format
print(old_date.strftime("%m/%d/%y"))

#2
from datetime import date, timedelta

today = date.today()
yesterday = today - timedelta(1)
tomorrow = today + timedelta(1)

print("Yesterday was:", yesterday.strftime("%D"))
print("Today is:", today.strftime("%D"))
print("Tomorrow will be:", tomorrow.strftime("%D"))

#3
from datetime import datetime

date = datetime.now()

date1 = date.replace(microsecond = 0)
print(date1)

"""
or
print(date.strftime("%Y-%m-%d %H:%M:%S"))
"""

#4
from datetime import datetime

date1 = datetime(2021, 2, 15, 20, 00, 00)
date2 = datetime(2021, 2, 17, 21, 00, 00)

diff = date2 - date1

print(diff.total_seconds())