#
# import CSVParser
# import os
#
#
#
# csvfile = CSVParser.CSVParser(fileRoute=os.path.join('data', '2020'), fileName='國道5號北向.csv')
# csvfile.readCSVfile(method='normal') #readCSVfile
# print("123")

import bisect  # import module
a = [2, 4, 6, 8, 10, 12, 14]  # list of integers in ascending order
x = 2  # number to insert
i = bisect.bisect_left(a, x)  # call method
print(i)
c = bisect.bisect_right(a, x)
print(c)

