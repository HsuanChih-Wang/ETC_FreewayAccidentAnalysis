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

a = {'r': 4}


# def find(allItems, id):
#     return allItems[id]
#
# def addItem(allItems, item):
#     allItems[item['id']] = item
#
# # create a python dictionary called `allItems`
# allItems = {}
#
# # add some items to the dictionary
# item1 = { 'id': 1, 'name': 'James' }
# item2 = { 'id': 2, 'name': 'Susan' }
# addItem(allItems, item1)
# addItem(allItems, item2)
#
# # now lookup an item by its id
#
# result = find(allItems, 1)
# print(result['name'])  # ==> 'James'

# nums1 = {'2020-02-10 00:00,01F0005N,N,31,10', '2020-02-10 00:00,01F0017N,N,32,5'}
# nums2 = {'2020-02-10 00:00,01F0005N,N,31'}
# print(nums1.intersection(nums2))
# print(nums2.intersection(nums1))

# x = '2020-02-10 00:00'
# y = '2020/02/10 00:00'
# from datetime import datetime
# if datetime.strptime(x, '%Y-%m-%d %H:%M') == datetime.strptime(y, '%Y/%m/%d %H:%M'):
#     print("true")
import numpy as np
import pandas as pd

x = np.array(['五結', '員山', '四堵', '坪林', '大園',
          '平鎮', '打鐵坑', '新莊', '永和', '汐止',
          '湖口', '竹東', '蘆竹', '香山', '鶯歌'])

# for item in x:
#     print(item)

# for i in np.arange(10, 20):
#     print(i)

import calendar

print(calendar.monthrange(2022, 1)[1])
print("1111")
for day in np.arange(1, calendar.monthrange(2022, 1)[1]+1):
    print(day)


# x = np.array([])
# x = np.append(x, [1,2,3])
# print(x)
#
# v = np.array([i for i in np.arange(10)])
# m = np.array([i for i in np.arange(5)])
#
# result = v - m
# print(result)




print("days = ", calendar.monthrange(2022, 1))


