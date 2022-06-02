# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
from sklearn import svm, metrics
from sklearn.model_selection import train_test_split,cross_val_score

# Load ------------------------------------------
data1_0 = pd.read_csv("2016NewYear_etag.csv")
data1_1 = pd.read_csv("201611_etag.csv")

data2_0 = pd.read_csv("2017NewYear_etag.csv")
data2_1 = pd.read_csv("201711_etag.csv")

data3_0 = pd.read_csv("2018NewYear_etag.csv")
data3_1 = pd.read_csv("201811_etag.csv")

data1 = pd.concat([data1_0, data1_1])
data2 = pd.concat([data2_0,data2_1])
data3 = pd.concat([data3_0,data3_1])

data = pd.concat([data1,data2])
data = pd.concat([data,data3])

# Preprocessing----------------------------------
direct_mapping = {'N':0, 'S':1}
data['direction'] = data['direction'].map(direct_mapping)
data = data.drop(data.columns[0], axis = 1)

#轉換為類別型態..................

data["direction"] = data["direction"].astype("category")
data["holiday"] = data["holiday"].astype("category")
data["HOV"] = data["HOV"].astype("category")
data["vehicleType"] = data["vehicleType"].astype("category")
data["go_resort"] = data["go_resort"].astype("category")

#轉換為dummy.............
#data = pd.get_dummies(data,columns=["holiday","HOV","vehicleType"])

# etag_X = data.iloc[:,0:11]
# etag_y = data['go_resort']


data_sample = data.sample(n=2000)
etag_X = data_sample.iloc[:,0:11]
etag_y = data_sample['go_resort']


print("data_sample = ",data_sample)
print("etag_X = ",etag_X)
print("etag_Y = ",etag_y)

print("dtype = ",etag_X.dtypes)


#train_X, test_X, train_y, test_y = train_test_split(etag_X, etag_y, test_size = 0.3)
print('split finish!')

svc = svm.SVC(kernel='sigmoid', C=10)
accuracy = cross_val_score(svc,etag_X,etag_y,cv=5,scoring="accuracy")
F1 = cross_val_score(svc,etag_X,etag_y,cv=5,scoring="f1")
precision = cross_val_score(svc,etag_X,etag_y,cv=5,scoring="precision")
recall = cross_val_score(svc,etag_X,etag_y,cv=5,scoring="recall")

print("accuracy = ",accuracy)
print("accuracy_mean = ",accuracy.mean())
print("F1 = ",F1)
print("precision = ",precision)
print("recall = ",recall)
print("")




# svc_fit = svc.fit(train_X, train_y)

print('training finish!')

#test_y_predicted = svc.predict(test_X)
print('testing finish!')

#accuracy = metrics.accuracy_score(test_y, test_y_predicted)
#confusion_matrix = metrics.confusion_matrix(test_y,test_y_predicted)
#print(accuracy)
#print(confusion_matrix)